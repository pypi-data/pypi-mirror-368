from ml_golem.model_loading_logic.config_based_class import ConfigBasedClass
from file_golem import Config

class ConfigCopier(ConfigBasedClass):
    def __init__(self, args):
        super().__init__(args)
        self.new_config_name = args.copy_config


    def __call__(self):
        self.check_availability()
        print('Compiling config...')

        config = self.data_io.load_config(self.global_config_name)
        if 'parent' in config:
            del config['parent']
        
        config['compile_origin'] = self.global_config_name
        self.data_io.save_data(Config, data_args = {
            Config.CONFIG_NAME: self.new_config_name,
            Config.DATA: config})


    def check_availability(self):
        if self.data_io.is_file_present(Config, data_args = {
            Config.CONFIG_NAME: self.new_config_name}):
            raise Exception(f'Config file {self.new_config_name} already exists. Please delete it or choose a different name.')
        return