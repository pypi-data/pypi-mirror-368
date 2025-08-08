
from ml_golem.overleaf.overleaf_datatypes import ProjectDatatype, OverleafDatatype,OverleafDirectory
from file_golem import SpecialDataArgs
from ml_golem.base_classes.data_io_object import DataIOObject

class OverleafTransfer(DataIOObject):
    def __init__(self,args):
        super().__init__(args)
        self.overleaf_subdir = self.data_io.system_config.get(SpecialDataArgs.OVERLEAF_SUBDIR.value)
        if SpecialDataArgs.OVERLEAF_MAPPINGS.value not in self.data_io.system_config:
            raise Exception(f'No dict named {SpecialDataArgs.OVERLEAF_MAPPINGS.value} found in the system config')
        self.mappings = self.data_io.system_config.get(SpecialDataArgs.OVERLEAF_MAPPINGS.value)

    def __call__(self):


        overleaf_dir_path = self.data_io.get_data_path(OverleafDirectory, data_args={
            OverleafDirectory.OVERLEAF_SUBDIR: self.overleaf_subdir
        })
        git_pull_command = (
            f'cd {overleaf_dir_path} && '
            'git pull'
        )
        self.data_io.run_system_command(git_pull_command)

        self.transfer_data()

        git_push_command = (
            f'cd {overleaf_dir_path} && '
            'git add . && '
            'git commit -m \"updating progress\" && '
            'git push'
        )
        self.data_io.run_system_command(git_push_command)


    def transfer_data(self):
        for entry in self.mappings:
            project_base, overleaf_base = next(iter(entry.items()))
            self.data_io.transfer_data(
                ProjectDatatype,
                OverleafDatatype,
                source_data_args = {
                    ProjectDatatype.SYSTEM_CONFIG_SPECIFIED_PATH: project_base
                },
                target_data_args = {
                    OverleafDatatype.OVERLEAF_SUBDIR: self.overleaf_subdir,
                    OverleafDatatype.SYSTEM_CONFIG_SPECIFIED_PATH: overleaf_base
                })