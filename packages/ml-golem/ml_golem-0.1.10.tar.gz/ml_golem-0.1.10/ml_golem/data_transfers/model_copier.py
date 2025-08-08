from file_golem import FileGolem, FilePathEntries
from ml_golem.base_classes.data_io_object import DataIOObject
from ml_golem.datatypes import ModelCheckpoint




class ModelCopier(DataIOObject):
    def __init__(self, args):
        super().__init__(args)
        if args.system_transfer is None:
            raise Exception('No system transfer specified. Please provide a system transfer name in the args.')
        

        self.local_data_io =FileGolem(
            system_config_path=self.data_io.system_config_path,
            is_debug=args.debug,
        )

        self.copy_config_name = args.config_name



    def __call__(self):

        origin_configs, instantiate_module_names, is_external_configs,instantiate_configs, model_module_names = \
            self.data_io.extract_architecture_information(self.copy_config_name)
        copy_to_data_io = self._get_copy_to()
        copy_from_data_io = self._get_copy_from()
        for origin_config, instantiate_module_name in zip(origin_configs, instantiate_module_names):
            data_args = {
                ModelCheckpoint.CONFIG_NAME: origin_config,
                ModelCheckpoint.MODULE: instantiate_module_name,
                ModelCheckpoint.EPOCH: FilePathEntries.OPEN_ENTRY
            }

            for file_name, file_args in copy_from_data_io.get_file_iterator(
                ModelCheckpoint, 
                data_args=data_args,
                can_return_data_args=True):

                checkpoint_data = copy_from_data_io.load_data(
                    ModelCheckpoint,
                    data_args=file_args)
                
                file_args[ModelCheckpoint.DATA] = checkpoint_data
                
                copy_to_data_io.save_data(ModelCheckpoint,
                    data_args=file_args)

class ModelCopyOver(ModelCopier):

    def _get_copy_to(self):
        return self.data_io

    def _get_copy_from(self):
        return self.local_data_io
    

class ModelCopyBack(ModelCopier):

    def _get_copy_to(self):
        return self.local_data_io

    def _get_copy_from(self):
        return self.data_io