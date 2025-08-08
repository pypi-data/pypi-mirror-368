import time
import io
import os
from enum import Enum
from itertools import product
from omegaconf import OmegaConf
from file_golem import Config, FilePathEntries
from ml_golem.model_loading_logic.config_based_class import ConfigBasedClass
from ml_golem.datatypes import GridShellScript, GridSlurmScript, AbstractSlurmOutput, SlurmOutputStd, SlurmOutputErr
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from ml_golem.main_loop_logic.reserved_keywords import ReservedArgKeywords
from ml_golem.base_classes.data_io_object import DataIOObject
from ml_golem.main_loop_logic.main_loop_messages import MainLoopMessages


class GridJobExecutionStyle(Enum):
    SEQUENTIAL = 'sequential'
    SLURM = 'slurm'
    NONE = 'none'

    

class GridJobBuilder(ConfigBasedClass):
    def __init__(self,args):
        super().__init__(args,subconfig_keys=[ModelConfigKeywords.GRID_JOB.value])

        self.grid_job_readable_labels = self.config.get(ModelConfigKeywords.GRID_JOB_READABLE_LABELS.value,True)

        self.has_grid_debug = self.config.get(ModelConfigKeywords.GRID_DEBUG.value, False)
        self.grid_actions = self.config.get(ModelConfigKeywords.GRID_ACTIONS.value)
        if len(self.grid_actions) == 0:
            raise Exception('No grid actions provided')
        self.grid_job_style = self.config.get(ModelConfigKeywords.GRID_JOB_STYLE.value)

        if self.grid_job_style == GridJobExecutionStyle.SLURM.value:
            self.slurm_config = self.data_io.fetch_subconfig(
                self.config,
                subconfig_keys=[ModelConfigKeywords.GRID_SLURM_CONFIG.value])

        grid_job_params = self.config.get(ModelConfigKeywords.GRID_JOB_PARAMS.value,[])
        self.has_grid_job_params = (len(grid_job_params) != 0)
        if self.has_grid_job_params:
            #Should be of format [[grid_key_a, grid_key_b, ...], [grid_key_c, grid_key_d, ...], ...]
            self.all_joined_grid_job_params = {}
            grid_job_joins = self.config.get(ModelConfigKeywords.GRID_JOB_JOINS.value, [])
            join_key_set = set()
            for i in range(len(grid_job_joins)):
                join_keys = sorted(grid_job_joins[i])
                common_length = None
                for join_key in join_keys:
                    if join_key not in grid_job_params.keys():
                        raise ValueError(f'Grid job join key {join_key} not found in grid job parameters {grid_job_params.keys()}')
                    if join_key in join_key_set:
                        raise ValueError(f'Grid job join key {join_key} is duplicated in grid job joins {grid_job_joins}')
                    join_key_set.add(join_key)

                    if common_length is None:
                        common_length = len(grid_job_params[join_key])
                    elif common_length != len(grid_job_params[join_key]):
                        raise ValueError(f'Grid job join key {join_key} has a different length than the other join keys in {grid_job_joins[i]}')
                joined_params = [[self._parse_grid_job_param(grid_job_params[join_key])[j] for join_key in join_keys] for j in range(common_length)]
                self.all_joined_grid_job_params[tuple(join_keys)] = joined_params
                
            singlton_params = list(set(grid_job_params.keys() - join_key_set))
            for singleton in singlton_params:
                parsed_param = self._parse_grid_job_param(grid_job_params[singleton])
                self.all_joined_grid_job_params[tuple([singleton])] = [[p] for p in parsed_param]
            self.config_list = []


    def _parse_grid_job_param(self,param):
        if isinstance(param, str):
            if ('-' in param) and all(part.isdigit() for part in param.split('-')) and (len(param.split('-')) == 2):
                start, end = map(int, param.split('-'))
                parsed_param = list(range(start, end + 1))
            else:
                raise ValueError(f"Invalid grid job parameter format: {param}. Currently, we only support lists or ranges in the format 'start-end'.")
        else:
            parsed_param = param
        return parsed_param


    def __call__(self):
        print('Building grid search...')

        self.build_configs()

        if len(self.grid_actions) == 0:
            raise Exception('No grid actions provided')
        if self.grid_job_style == GridJobExecutionStyle.SEQUENTIAL.value:
            if not self.has_grid_job_params:
                raise Exception('Grid job style is sequential, but no grid job parameters provided. Therefore it is recommended to run the action directly in the terminal instead of using the grid search builder.')
            self.build_and_execute_sequential_shell_script()
        elif self.grid_job_style == GridJobExecutionStyle.SLURM.value:
            self.build_and_execute_slurm_script()
        else:
            raise Exception(f'Grid search style {self.grid_job_style} not recognized')

    def build_and_execute_slurm_script(self):
        slurm_script_file_name, total_array_length, log_dir_name = self.build_slurm_script()        
        array_args = f'-a 0-{total_array_length-1} ' if self.has_grid_job_params else ''
        slurm_command = f'sbatch {array_args}./{slurm_script_file_name}'

        slurm_server_output = self.ssh_to_slurm_and_execute(slurm_command)
        print(f'You can check the slurm logs in the directory: {log_dir_name}')
        self.slurm_job_id = int(slurm_server_output[0].split()[-1])  # Assuming the job number is the last part of the output


    def is_slurm_job_complete(self):
        slurm_command = f'squeue --job {self.slurm_job_id}'
        slurm_server_output = self.ssh_to_slurm_and_execute(slurm_command)
        if len(slurm_server_output) <= 1:
            return True
        else:
            return False

            
    def ssh_to_slurm_and_execute(self, slurm_server_command):
        slurm_command_buffer = io.StringIO()
        slurm_server_credentials, slurm_project_directory = self.data_io.get_slurm_server_credentials_and_project_directory()
        
        ssh_to_execute_command = (slurm_server_credentials is not None) and (slurm_project_directory is not None)
        if not ssh_to_execute_command:
            print(f'Warning: slurm server credentials or slurm project directory not provided. Will try calling slurm locally.')
        
        if ssh_to_execute_command:
            slurm_command_buffer.write(f'ssh {slurm_server_credentials} \" cd {slurm_project_directory} && ')
        slurm_command_buffer.write(slurm_server_command)
        if ssh_to_execute_command:
            slurm_command_buffer.write(f' && exit \"')
        command = slurm_command_buffer.getvalue()
        slurm_command_buffer.close()
        slurm_server_output, slurm_exit_code = self.data_io.run_system_command(command,return_output=True, return_exit_code=True )
        if slurm_exit_code != 0:
            raise Exception(f'SLURM command failed with exit code {slurm_exit_code}. Please check the console output to debug')
        return slurm_server_output


    def build_slurm_script(self):
        script_buffer = io.StringIO()
        script_buffer.write(f'#!/bin/bash\n')
        
        partition = self.slurm_config.get('partition', 'a100')
        script_buffer.write(f'#SBATCH --partition={partition}\n')

        gpu = self.slurm_config.get('gpu', 0)
        script_buffer.write(f'#SBATCH --gres=gpu:{gpu}\n')

        cpu = self.slurm_config.get('cpu',1)
        script_buffer.write(f'#SBATCH -c {cpu}\n')

        time = self.slurm_config.get('time','01:00:00')
        script_buffer.write(f'#SBATCH -t {time}\n')

        memory = self.slurm_config.get('memory', '1G')
        script_buffer.write(f'#SBATCH --mem={memory}\n')

        data_args = {
            GridSlurmScript.CONFIG_NAME: self.global_config_name,
        }

        slurm_output_directory = self.data_io.get_data_path(SlurmOutputStd,data_args = data_args)
        self.data_io.create_directory(slurm_output_directory)
        script_buffer.write(f'#SBATCH -o {slurm_output_directory}\n')

        slurm_error_directory = self.data_io.get_data_path(SlurmOutputErr,data_args = data_args)
        script_buffer.write(f'#SBATCH -e {slurm_error_directory}\n')
        script_buffer.write(f'eval "$(conda shell.bash hook)"\n')
        script_buffer.write(f'conda activate {self.data_io.get_base_conda_name()}\n')

        if self.has_grid_job_params:
            grid_array_lengths = [len(array) for array in self.all_joined_grid_job_params.values()]
            for i in range(len(grid_array_lengths)):
                
                modulus= grid_array_lengths[i]
                divisor = 1
                for j in range(i + 1,len(grid_array_lengths)):
                    divisor *= grid_array_lengths[j]

                script_buffer.write( f'i_{i}=$(( ($SLURM_ARRAY_TASK_ID / {divisor}) % {modulus} ))\n')

                if self.grid_job_readable_labels:
                    #Add in the logic to get the readable labels for the grid job parameters
                    for j in range(modulus):
                        if j == 0:
                            script_buffer.write('if ')
                        else:
                            script_buffer.write('elif ')
                        
                        script_buffer.write(f'[ $i_{i} -eq {j} ]\n')
                        script_buffer.write(f'then\n')
                        readable_label = Config._get_parameter_for_config_name(
                            self.all_joined_grid_job_params,
                            i, j)
                        script_buffer.write(f'\ti_{i}=\"{readable_label}\"\n')
                    script_buffer.write('fi\n')
            config_file = self.data_io.get_data_path(Config, data_args={
                Config.CONFIG_NAME: self.global_config_name,
                Config.GRID_IDX: [f'${{i_{i}}}' for i in range(len(grid_array_lengths))],
            })
            self._write_command_into_script(script_buffer, config_file)

            total_array_length = 1
            for array_length in grid_array_lengths:
                total_array_length *= array_length
        else:
            config_file = self.data_io.get_data_path(Config, data_args={
                Config.CONFIG_NAME: self.global_config_name,
            })
            self._write_command_into_script(script_buffer, config_file)
            total_array_length = 1


        log_dir_name = os.path.dirname(slurm_output_directory)
        return self._save_script_and_return_path(script_buffer,GridSlurmScript) ,total_array_length, log_dir_name

    def config_info_iterator(self):
        data_args = {
            Config.CONFIG_NAME: self.global_config_name,
        }
        if self.grid_job_readable_labels:
            data_args[Config.GRID_IDX_LABELS] = self.all_joined_grid_job_params

        for array_combo, grid_indices in zip(product(*self.all_joined_grid_job_params.values()), product(*[range(len(array)) for array in self.all_joined_grid_job_params.values()])):
            grid_args = dict(zip(self.all_joined_grid_job_params.keys(), array_combo))
            data_args[Config.GRID_IDX]=grid_indices
            yield data_args, grid_args

    def build_configs(self):
        if not self.has_grid_job_params:
            return
        for config_data_args, grid_args in self.config_info_iterator():
            override_config = OmegaConf.create({
                ModelConfigKeywords.GRID_JOB.value: OmegaConf.create({
                    ModelConfigKeywords.GRID_JOB_MAIN_CONFIG.value:self.global_config_name,
                }),
                'defaults': [self.global_config_name],
            })
            for config_keys, config_values in grid_args.items():
                for config_key, config_value in zip(list(config_keys), config_values):
                    if config_key == 'defaults':
                        override_config['defaults'] = [config_value] + override_config['defaults']
                    else:
                        #TODO: account for the case where a list config is passed, not just a dict. This can occur when there are many models modules. 
                        key_split = config_key.split('.')
                        nested_config_condition = {}
                        current = nested_config_condition
                        for key in key_split[:-1]:  
                            current = current.setdefault(key, {}) 
                        current[key_split[-1]] = config_value
                        override_config = OmegaConf.merge(override_config, OmegaConf.create(nested_config_condition))

            config_data_args[Config.DATA]= override_config
            self.data_io.save_data(Config, data_args = config_data_args)
            config_file_name = self.data_io.get_data_path(Config, data_args = config_data_args)
            self.config_list.append(config_file_name)        

    def build_and_execute_sequential_shell_script(self):
        shell_script_file_name = self.build_shell_script()
        command = f'./{shell_script_file_name}'
        self.data_io.run_system_command(command)

    def build_shell_script(self):
        script_buffer = io.StringIO()
        script_buffer.write(f'#!/bin/bash\n')
        for config_file in self.config_list:
            self._write_command_into_script(script_buffer, config_file)
        return self._save_script_and_return_path(script_buffer,GridShellScript)
    

    def _write_command_into_script(self,script_buffer, config_file):

        for action_code in self.grid_actions:
            if (action_code == ReservedArgKeywords.INFER.value) or \
                (action_code == ReservedArgKeywords.INFER_SHORT.value) or \
                (action_code == ReservedArgKeywords.TRAIN.value) or \
                (action_code == ReservedArgKeywords.TRAIN_SHORT.value):


                #/BRAIN/mmbt/static00/envs/mmbt/bin/accelerate
                base_conda_name = self.data_io.get_base_conda_name()
                script_buffer.write(f'{base_conda_name}/bin/accelerate launch')
                if self.grid_job_style == GridJobExecutionStyle.SLURM.value:
                    gpu = self.slurm_config.get('gpu', 0)
                    if gpu > 1:
                        script_buffer.write(' --multi_gpu')
                        print('WARNING: Using multi_gpu mode with SLURM, you will likely encounter port in use errors.')
                        print('Support for this is not implemented yet.')
                        print('A partial solution is to use the  --main_process_port to specify a port that is not in use.')
                        print('However, dev is still on going')
            else:
                script_buffer.write('python')

            script_buffer.write(f' main.py --{action_code} -c {config_file}')
            if self.has_grid_debug:
                script_buffer.write(f' --{ReservedArgKeywords.DEBUG.value}')
            script_buffer.write('\n')
            script_buffer.write(f'echo ""\n')
    
    def _save_script_and_return_path(self,script_buffer,script_class):
        script = script_buffer.getvalue()
        script_buffer.close()
        data_args = {
            script_class.CONFIG_NAME: self.global_config_name,
            script_class.DATA: script}
        
        self.data_io.save_data(script_class, data_args = data_args)
        script_file_name = self.data_io.get_data_path(script_class, data_args = data_args)
        return script_file_name
    
    def get_count_of_grid_jobs(self):
        if not self.has_grid_job_params:
            return 1
        return len(self.config_list)


class GridJobViewer(GridJobBuilder):
    def __init__(self,args):
        super().__init__(args)

    def __call__(self):
        self.print_slurm_outputs()
        self.print_slurm_errors()


    def _get_latest_timestamp(self):
        if self.grid_job_style != GridJobExecutionStyle.SLURM.value:
            raise Exception(f'Grid job viewer can only be used with SLURM style grid jobs, but got {self.grid_job_style}')
        latest_directory = None
        latest_timestamp = None
        for slurm_output_directory, data_args in self.data_io.get_file_iterator(AbstractSlurmOutput,
            data_args = {
                AbstractSlurmOutput.CONFIG_NAME: self.global_config_name,
                AbstractSlurmOutput.TIMESTAMP: FilePathEntries.OPEN_ENTRY},
            can_return_data_args= True,
            ):
            latest_directory = slurm_output_directory
            latest_timestamp = data_args[AbstractSlurmOutput.TIMESTAMP]

        if latest_directory is None:
            raise Exception(f'No SLURM output directory found for config {self.global_config_name}. Please run the grid job first.')

        return latest_timestamp
        
    def print_slurm_outputs(self):
        latest_timestamp = self._get_latest_timestamp()
        print('SLURM outputs:')
        for slurm_output in self.data_io.get_file_iterator(SlurmOutputStd, data_args = {
            SlurmOutputStd.CONFIG_NAME: self.global_config_name,
            SlurmOutputStd.TIMESTAMP: latest_timestamp,
            SlurmOutputStd.SLURM_FORMAT_FILENAME: FilePathEntries.OPEN_ENTRY}):
            print(slurm_output)

    def print_slurm_errors(self):
        print('SLURM errors:')
        latest_timestamp = self._get_latest_timestamp()
        for slurm_error in self.data_io.get_file_iterator(SlurmOutputErr, data_args = {
            SlurmOutputErr.CONFIG_NAME: self.global_config_name,
            SlurmOutputErr.TIMESTAMP: latest_timestamp,
            SlurmOutputErr.SLURM_FORMAT_FILENAME: FilePathEntries.OPEN_ENTRY}):
            yield slurm_error



class SequentialGridJobExecutor(DataIOObject):
    def __init__(self,args):
        super().__init__(args)
        self.check_every = 600 # Check every ten minutes for job completion 10 minutes
        self.all_configs = args.sequential_grid_job
        self.save_args = args

    def __call__(self):
        for config_name in self.all_configs:
            self.save_args.config_name = config_name
            grid_job_builder = GridJobBuilder(self.save_args)
            if grid_job_builder.grid_job_style != GridJobExecutionStyle.SLURM.value:
                raise Exception(f'Sequential grid job executor can only be used with SLURM style grid jobs (for now...). ')
            
            grid_job_builder()
            total_config_count = grid_job_builder.get_count_of_grid_jobs()
            slurm_job_indices = [-1] if total_config_count == 1 else list(range(total_config_count))
            slurm_job_id = grid_job_builder.slurm_job_id

            latest_timestamp = GridJobViewer(self.save_args)._get_latest_timestamp()


            while True:
                time.sleep(self.check_every)
                is_slurm_job_complete = grid_job_builder.is_slurm_job_complete()
                #Check if slurm job is off
                if is_slurm_job_complete:
                    for job_index in slurm_job_indices:
                        slurm_file_args = {
                            AbstractSlurmOutput.CONFIG_NAME: config_name,
                            AbstractSlurmOutput.SLURM_JOB_ID: slurm_job_id,
                            AbstractSlurmOutput.SLURM_ARRAY_TASK_ID: job_index,
                            AbstractSlurmOutput.TIMESTAMP: latest_timestamp,
                        }

                        if not self.data_io.is_file_present(SlurmOutputStd, data_args = slurm_file_args):
                            missing_filename = self.data_io.get_data_path(SlurmOutputStd, data_args = slurm_file_args)
                            raise Exception(f'SLURM job {job_index} is complete, but the output file {missing_filename} is missing. This may indicate that the job did not run or failed to produce output.')

                        
                        slurm_file_args[SlurmOutputStd.LAST_LINES] = 1
                        last_line = self.data_io.load_data(SlurmOutputStd, data_args = slurm_file_args)
                        if last_line != MainLoopMessages.COMPLETE_PROGRAM.value:
                            slurm_file_args[SlurmOutputErr.LAST_LINES] = 10
                            if self.data_io.is_file_present(SlurmOutputErr, data_args = slurm_file_args):
                                last_error_lines = self.data_io.load_data(SlurmOutputErr, data_args = slurm_file_args)
                                
                                print('last line was:', last_line)
                                if job_index == -1:
                                    print(f'last error lines for {slurm_job_id}:')
                                else:
                                    print(f'last error lines for {slurm_job_id} job index {job_index}:')
                                for line in last_error_lines:
                                    print(line)
                            else:
                                missing_error_filename = self.data_io.get_data_path(SlurmOutputErr, data_args = slurm_file_args)
                                print(f'No error log {missing_error_filename} produced.')                            
                            raise Exception(f'SLURM job for config {config_name} did not complete successfully. See the above lines for details')
                    break
