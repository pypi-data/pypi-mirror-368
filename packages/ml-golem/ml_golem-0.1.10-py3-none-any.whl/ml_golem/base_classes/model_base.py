import torch.nn as nn
from ml_golem.base_classes._helper_functions import _unwrap_module
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from ml_golem.model_loading_logic.config_based_class import ConfigBasedClass


### Use this class for models in your pipeline that are NOT based on PyTorch.
### This will still enable cross talk with PyTorch models, but will not inherit from nn.Module.
### This is useful for models that are not based on PyTorch, such as scikit-learn models or other libraries.
### If you want to use PyTorch models, use ModelBase instead
class ModuleAccessingConfigBasedClass(ConfigBasedClass):
    def __init__(self, args, subconfig_keys):
        ConfigBasedClass.__init__(self, args, subconfig_keys)
        self.model_module_names = None
        self.models = None

    def _set_module_names_and_pointers(self,module_names,models):
        """
        Set the module names and pointers to other models.
        This is useful for accessing other models in the same run.
        """
        self.model_module_names = module_names
        self.models = models
    
    def get_module_by_name(self,module_name):
        name_idx = self.model_module_names.index(module_name)
        module = self.models[name_idx]
        unwrapped_module = _unwrap_module(module)
        return unwrapped_module


class ModelBase(ModuleAccessingConfigBasedClass,nn.Module):
    def __init__(self,args,subconfig_keys):
        ModuleAccessingConfigBasedClass.__init__(self, args, subconfig_keys)
        nn.Module.__init__(self)
        self.resume_epoch = None
        self.is_frozen = self.data_io.fetch_config_field(self.config, subconfig_keys=[ModelConfigKeywords.IS_FROZEN.value], default=False)


    def _is_frozen(self):
        return self.is_frozen

    def _set_device(self, device):
        self.device = device

    # Call this method to get the device on which the model is currently located
    def _get_device(self):
        return self.device

    def _set_resume_epoch(self, epoch):
        self.resume_epoch = epoch

    # Call this method to get the epoch from which the model resumed training or inference
    def _get_resume_epoch(self):
        return self.resume_epoch    