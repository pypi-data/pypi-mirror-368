from file_golem import FileDatatypes,AbstractDatatype,FilePathEntries
from file_golem import Config, SpecialDataArgs

class ModelCheckpoint(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.TORCH_CHECKPOINT
    EPOCH = 'epoch'
    MODULE = 'module'
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        'model_checkpoints',
        FilePathEntries.CONFIG_ENTRY,
        {FilePathEntries.CUSTOM_LOGIC: '_include_module_entry'},
        {FilePathEntries.DATA_ARG_ENTRY: EPOCH})
    
    @staticmethod
    def _include_module_entry(data_args):
        if ModelCheckpoint.MODULE not in data_args:
            return None
        module = data_args[ModelCheckpoint.MODULE]
        if module == FilePathEntries.OPEN_ENTRY:
            return '*'
        return module

    @staticmethod
    def _retrieve_data_args(relative_path_tuple, data_args):
        args_to_return = {
            ModelCheckpoint.EPOCH: relative_path_tuple[-1],
            ModelCheckpoint.CONFIG_NAME: data_args.get(ModelCheckpoint.CONFIG_NAME, None),
            ModelCheckpoint.MODULE: data_args.get(ModelCheckpoint.MODULE, None)
        }
        return args_to_return


class TrainingLog(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.EMPTY
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        'training_logs',
        FilePathEntries.CONFIG_ENTRY)



class EvaluationResults(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.JSON
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        'evaluation_log',)


class GridShellScript(Config):
    FILE_DATATYPE = FileDatatypes.SHELL
    IS_EXECUTABLE = True  # Shell scripts are executable
    RELATIVE_PATH_TUPLE = Config.RELATIVE_PATH_TUPLE + ('_sequential_job',)


class GridSlurmScript(Config):
    FILE_DATATYPE = FileDatatypes.SLURM_SCRIPT
    IS_EXECUTABLE = True  # Slurm scripts are executable
    RELATIVE_PATH_TUPLE = Config.RELATIVE_PATH_TUPLE + ('_slurm_job',)


### SLURM OUTPUTS
class AbstractSlurmOutput(AbstractDatatype):
    SLURM_FORMAT_FILENAME = 'slurm_format_filename'
    FILE_DATATYPE = FileDatatypes.EMPTY
    LAST_LINES = 'last_lines'
    SLURM_JOB_ID = 'slurm_job_id'
    SLURM_ARRAY_TASK_ID = 'slurm_array_task_id'
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        'misc',
        'slurm',
        FilePathEntries.TIMESTAMP_CONFIG_ENTRY,)
        #'%j')
        # 
    @staticmethod
    def _retrieve_data_args(relative_path_tuple, data_args):
        config_timestamp_entry = relative_path_tuple[-1]
        timestamp = config_timestamp_entry[-data_args[SpecialDataArgs.DATA_IO]._get_timestamp_format_size():]
        data_args[AbstractSlurmOutput.TIMESTAMP] = timestamp
        return data_args
    
    @staticmethod
    def _slurm_format_or_open_entry(data_args):

        if AbstractSlurmOutput.SLURM_JOB_ID in data_args:
            job_id = data_args[AbstractSlurmOutput.SLURM_JOB_ID]
            if job_id == FilePathEntries.OPEN_ENTRY:
                job_prefix = '*'
            else:
                job_prefix = f'{job_id}'
            if AbstractSlurmOutput.SLURM_ARRAY_TASK_ID in data_args:
                task_id = data_args[AbstractSlurmOutput.SLURM_ARRAY_TASK_ID]
                if task_id == FilePathEntries.OPEN_ENTRY:
                    job_index_suffix = '_*'
                elif task_id == -1:
                    job_index_suffix = ''
                else:
                    job_index_suffix = f'_{task_id}'
            return f'{job_prefix}{job_index_suffix}'

            
        if AbstractSlurmOutput.SLURM_FORMAT_FILENAME in data_args:
            file_name = data_args[AbstractSlurmOutput.SLURM_FORMAT_FILENAME]
            if file_name != FilePathEntries.OPEN_ENTRY:
                raise Exception('Can only use slurm format filename with open entry')
            return '*'
        else:
            return '%A_%a'
    
class SlurmOutputStd(AbstractSlurmOutput):
    FILE_DATATYPE = FileDatatypes.SLURM_OUTPUT_STD
    RELATIVE_PATH_TUPLE = AbstractSlurmOutput.RELATIVE_PATH_TUPLE + (
         {FilePathEntries.CUSTOM_LOGIC: '_slurm_format_or_open_entry'},)


class SlurmOutputErr(AbstractSlurmOutput):
    FILE_DATATYPE = FileDatatypes.SLURM_OUTPUT_ERR
    RELATIVE_PATH_TUPLE = AbstractSlurmOutput.RELATIVE_PATH_TUPLE + (
         {FilePathEntries.CUSTOM_LOGIC: '_slurm_format_or_open_entry'},)
