from ml_golem.base_classes.data_io_object import DataIOObject

from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords


class ConfigBasedClass(DataIOObject):
    def __init__(self,args,subconfig_keys=[]):
        super().__init__(args)
        self.is_inference = args.infer
        self.is_training = args.train

        self.subconfig_keys = subconfig_keys
        self.global_config_name = args.config_name
        if 'local_config_name' in args:
            self.local_config_name = args.local_config_name
        else:
            self.local_config_name = self.global_config_name

        if 'origin_config_name' in args:
            self.origin_config_name = args.origin_config_name

        if 'object_ancestry' in args:
            self.object_ancestry = args.object_ancestry

        self.config = self.data_io.fetch_subconfig(
            self.local_config_name,
            subconfig_keys= subconfig_keys)
        

    def _get_grid_job_main_config_name(self):
        grid_job_main_config_name = self.data_io.fetch_config_field(
            self.global_config_name,
            subconfig_keys=[ModelConfigKeywords.GRID_JOB.value, ModelConfigKeywords.GRID_JOB_MAIN_CONFIG.value],)
        
        return grid_job_main_config_name
        
        
    def _get_ancestor(self):
        """
        Returns the ancestor object if it exists, otherwise returns self.
        This is useful for accessing the config of the ancestor object.
        """
        return self.object_ancestry[-1]
    
    def _get_local_config(self):
        """
        Returns the local config of the current object.
        This is useful for accessing the config of the current object.
        """
        return self.config

    def instantiate_config_based_class(self,args,config_or_config_name,subconfig_keys,default_class=None,origin_config=None):
        if len(subconfig_keys) == 0:
            if config_or_config_name == self.config:
                print('A non-zero length list subconfig_keys must be provided to instantiate a config based class, if the configs are the same. ')
                print('In this situation, it is best practice to add levels to your config')
                print('You can access a the instantiator classes config by calling ._get_ancestor()._get_local_config() ')
                raise Exception('Empty subconfig_keys provided to instantiate_config_based_class. See warnings above.')
        
        config_class =self.data_io.fetch_class_from_config(
            config_or_config_name,
            subconfig_keys = subconfig_keys + [ModelConfigKeywords.MODEL_CLASS.value],
            default = default_class)

        if config_class is None:
            raise Exception(f'No class found for keys {subconfig_keys + [ModelConfigKeywords.MODEL_CLASS.value]} in config {config_or_config_name}')  


        args.origin_config_name =  self.global_config_name if origin_config is None else origin_config
        args.local_config_name = config_or_config_name
        if hasattr(self,'object_ancestry'):
            args.object_ancestry = [*self.object_ancestry,self]
        else:
            args.object_ancestry = [self]


        instantiated_class = config_class(args, subconfig_keys)

        if 'local_config_name' in args:
            del args.local_config_name

        if 'origin_config_name' in args:
            del args.origin_config_name

        if 'object_ancestry' in args:
            del args.object_ancestry
        return instantiated_class
