import torch
import torch.nn as nn
from accelerate import Accelerator
from file_golem import FilePathEntries
from ml_golem.base_classes._helper_functions import _unwrap_module
from ml_golem.datatypes import ModelCheckpoint
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from ml_golem.base_classes.dataloading_base import DataIterationBase
from ml_golem.base_classes.model_base import ModelBase
from ml_golem.base_classes.model_base import ModuleAccessingConfigBasedClass



##Possible patterns:
# architecture:
#   module_list:
#       model_class: ...

#architecture: 
#   module_list:
#       origin_config: <config_name>
#       (opt) origin_module: <module_1, or module_2, ...>
#       resume_epoch: <n>

# architecture:
#   module_list:
#       -module_1:
#         model_class: ...
#       -module_2:
#         model_class: ...
#  ....

# architecture:
#   module_list:
#       -module_1:
#           origin_config: <config_name>
#           resume_epoch: <n>
#           (opt) origin_module: <module_1, or module_2, ...>
#       -module_2: <config_name>
#           origin_config: <config_name>
#           resume_epoch: <n>
#           (opt) origin_module: <module_1, or module_2, ...>
# ..




class ModelIOBase(DataIterationBase):

    def __init__(self, args,subconfig_keys):
        super().__init__(args,subconfig_keys)
        self._seed_torch(args)
        ###Autocasting paramters
        self.can_autocast = self.data_io.fetch_config_field(self.config, subconfig_keys=[ModelConfigKeywords.AUTOCASTING.value, ModelConfigKeywords.CAN_AUTOCAST.value], default=False)
        self.autocast_dtype = self.data_io.fetch_config_field(self.config, subconfig_keys=[ModelConfigKeywords.AUTOCASTING.value,ModelConfigKeywords.AUTOCAST_DTYPE.value], default=None)
        self.autocast_cache_enabled = self.data_io.fetch_config_field(self.config, subconfig_keys=[ModelConfigKeywords.AUTOCASTING.value,ModelConfigKeywords.AUTOCAST_CACHE_ENABLED.value], default=True)

        ##Extract all relevant information from the architecture
        origin_configs, instantiate_module_names, self.is_external_configs,instantiate_configs, self.model_module_names = \
            self.data_io.extract_architecture_information(self.global_config_name)
        
        self.models = []
        for instantiate_config, origin_config, instantiate_module_name in zip(instantiate_configs, origin_configs, instantiate_module_names):
            model_module = self.instantiate_config_based_class(
                args,
                instantiate_config, 
                subconfig_keys = [],
                origin_config = origin_config)
            
            if isinstance(model_module, nn.Module) and model_module._is_frozen():
                model_module.requires_grad_(False)

            origin_configs.append(origin_config)
            instantiate_module_names.append(instantiate_module_name)
            self.models.append(model_module)

        self._set_module_order()

        self.resume_epoch = int(self.data_io.fetch_config_field(
            self.config,
            subconfig_keys = [ModelConfigKeywords.RESUME_EPOCH.value],
            default=-1))
        
        if self.resume_epoch == -1: #Look for the latest checkpoint
            #Find the correct resume epoch for the global config.
            for model, instantiate_module_name, is_external_config in zip(self.models, instantiate_module_names, self.is_external_configs):
                if is_external_config:
                    continue
                if isinstance(model, nn.Module):
                    unwrapped_model = _unwrap_module(model)
                    if unwrapped_model._is_frozen():
                    #if model._is_frozen():
                        print(f'Skipping finding resume epoch for module {instantiate_module_name}. Module is frozen.')
                        continue
                    print('entring checkpoint search: ', instantiate_module_name)
                    for _, file_args in self.data_io.get_file_iterator(
                        ModelCheckpoint,
                        data_args = {
                            ModelCheckpoint.CONFIG_NAME: self.global_config_name,
                            ModelCheckpoint.EPOCH: FilePathEntries.OPEN_ENTRY,
                            ModelCheckpoint.MODULE: instantiate_module_name,
                        },
                        can_return_data_args=True):
                        new_epoch = int(file_args[ModelCheckpoint.EPOCH])
                        if new_epoch > self.resume_epoch:
                            self.resume_epoch = new_epoch
                    break #We found the latest checkpoint for the global config, no need to check other modules



        for model,origin_config, instantiate_module_name, is_external_config, module_name \
            in zip(self.models, origin_configs, instantiate_module_names, self.is_external_configs, self.model_module_names):
            

            if isinstance(model, ModuleAccessingConfigBasedClass):
                #Set pointers to other models if needed
                model._set_module_names_and_pointers(self.model_module_names,self.models)
            else:
                print(f'Warning: model {instantiate_module_name} is not a ModuleAccessingConfigBasedClass, skipping setting module names and pointers.')

            if not isinstance(model, nn.Module):
                string_name = '' if module_name is None else {module_name}
                print(f'Skipping loading for module {string_name} with config {origin_config}. This module is not a nn.Module and will not be loaded from checkpoint.')
                continue
            
            unwrapped_model = _unwrap_module(model)
            if (unwrapped_model._is_frozen() or self.resume_epoch == -1) and is_external_config: #In these cases we insist on the user specifying the resume epoch. This could be made more flexible in the future.
                subconfig_keys = self.data_io._create_origin_subconfig_keys(module_name)
                subconfig_keys.append(ModelConfigKeywords.RESUME_EPOCH.value)
                module_resume_epoch = self.data_io.fetch_config_field(
                    self.global_config_name,
                    subconfig_keys = subconfig_keys)
            elif unwrapped_model._is_frozen(): #Model is frozen, but not external config. This assumption is that weights have already been loaded and the model is not being trained.
                module_resume_epoch = -1
            else:
                module_resume_epoch = self.resume_epoch

            self._print_resume_epoch_message(module_name,origin_config, module_resume_epoch)

            if module_resume_epoch != -1:
                skip_loading = self.data_io.fetch_config_field(self.config,
                    subconfig_keys = [ModelConfigKeywords.SKIP_LOADING.value],
                    default=False)
                if not skip_loading:
                    model_checkpoint = self.data_io.load_data(ModelCheckpoint, data_args = {
                        ModelCheckpoint.CONFIG_NAME: origin_config, #self.global_config_name,
                        ModelCheckpoint.MODULE: instantiate_module_name,
                        ModelCheckpoint.EPOCH: module_resume_epoch
                    })
                    model.load_state_dict(model_checkpoint)
                else:
                    print(f'Skipping loading for module {module_name} with config {origin_config}. This module is set to skip loading.')
            model._set_resume_epoch(max(0,self.resume_epoch))
        
        self.resume_epoch = max(0,self.resume_epoch) #Ensure the resume epoch is not negative
        print(f'Model run will begin at epoch {self.resume_epoch}')

        self.dataloader = self._initialize_dataloader(args,self.subconfig_keys)



    def _set_module_order(self):
        module_order_from_config = self.data_io.fetch_config_field(
            self.global_config_name,
            subconfig_keys=[ModelConfigKeywords.ARCHITECTURE.value, ModelConfigKeywords.MODULE_ORDER.value],
            default=None)
        
        if module_order_from_config is None:
            self.module_order = self.models
        else:
            self.module_order = []
            for module_name in module_order_from_config:
                if module_name in self.model_module_names:
                    index = self.model_module_names.index(module_name)
                    self.module_order.append(self.models[index])
                else:
                    raise Exception(f'Module name {module_name} not found in model module names {self.model_module_names}. Please check the configuration.')

    def _seed_torch(self,args):
        seed = args.seed
        torch.manual_seed(seed)  # CPU
        torch.cuda.manual_seed(seed)  # GPU
        torch.cuda.manual_seed_all(seed)  # All GPUs (if using multiple GPUs)
        #Other Potential Calls:
        # random.seed(seed)  # Python's random module
        # np.random.seed(seed)  # NumPy
        # torch.backends.cudnn.deterministic = True  # Enforce deterministic behavior for GPU operations
        # torch.backends.cudnn.benchmark = False  # Disable auto-tuning for deterministic behavior

    def _call_core_function_with_autocast(self,func):
        if self.can_autocast:
            if self.autocast_dtype is None:
                with torch.amp.autocast(self.accelerator.device.type, enabled=self.autocast_cache_enabled):
                    func()
            else:
                dtype = getattr(torch, self.autocast_dtype)
                with torch.amp.autocast(self.accelerator.device.type, enabled=self.autocast_cache_enabled, dtype=dtype):
                    func()
        else:
            func()


    def _print_resume_epoch_message(self, module_name,instantiate_config, resume_epoch):
        string_name = '' if module_name is None else module_name
        if resume_epoch == -1:
            resume_epoch_message = 'no checkpoint found, initializing from scratch'
        else:
            resume_epoch_message = f'fetching checkpoint from epoch {resume_epoch}'
        print(f'For module {string_name} with config {instantiate_config}, {resume_epoch_message}')


    def _create_origin_subconfig_keys(self, module_name=None):
        subconfig_keys = [ModelConfigKeywords.ARCHITECTURE.value, ModelConfigKeywords.MODULE_LIST.value]
        if module_name is not None:
            subconfig_keys.append(module_name)
        return subconfig_keys

    def _can_prepare_accelerator(self):
        can_prepare = False
        for model_module in self.models:
            if isinstance(model_module, nn.Module):
                can_prepare = True
                break
        return can_prepare
    

    def _prepare_accelerator(self):
        if not self._can_prepare_accelerator():
            print('No nn.Module found, skipping accelerator preparation')
            self.is_module_wrapped_by_accelerator = [False] * len(self.models)
            return
        self.accelerator = Accelerator()

        self.is_module_wrapped_by_accelerator = []

        #for i in range(len(self.models)):
        for i, model in enumerate(self.models):
            if not isinstance(self.models[i], nn.Module):
                self.is_module_wrapped_by_accelerator.append(False)
                continue
            can_set_device = issubclass(type(self.models[i]), ModelBase)
            original_model_type = type(self.models[i])
            self.models[i] = self.accelerator.prepare(self.models[i])
            accelerator_model_type = type(self.models[i])

            self.is_module_wrapped_by_accelerator.append(original_model_type != accelerator_model_type)

            if can_set_device:
                unwrapped_model = _unwrap_module(model)
                unwrapped_model._set_device(self.accelerator.device)

                #callable_model = self._get_callable_model(i)
                #callable_model._set_device(self.accelerator.device)

        if hasattr(self, 'dataloader') and isinstance(self.dataloader, torch.utils.data.DataLoader):
            self.dataloader = self.accelerator.prepare(self.dataloader)


        if hasattr(self,'optimizer'):
            self.optimizer = self.accelerator.prepare(self.optimizer)
        if hasattr(self,'loss'):
            self.loss = self.accelerator.prepare(self.loss)
        if hasattr(self,'validation_dataloader'):
            self.validation_dataloader = self.accelerator.prepare(self.validation_dataloader)
        if hasattr(self,'validation_loss'):
            self.validation_loss = self.accelerator.prepare(self.validation_loss)


    def make_forward_pass(self,input_data=None):
        is_first = True
        #for model_module in self.models:
        for model_module in self.module_order:
            if is_first and (input_data is None):
                is_first = False
                output_data = model_module()
            else:
                output_data = model_module(input_data)
            input_data = output_data
        return output_data


    # def _get_callable_model(self,index):
    #     model = self.models[index]
    #     if self.is_module_wrapped_by_accelerator[index]:
    #         return model.module
    #     return model



    def switch_model_to_train(self):
        print('Switching models to training mode.')
        for module in self.models:
            if isinstance(module, nn.Module):
                module.train()

    def switch_model_to_eval(self):
        for model_module in self.models:
            if isinstance(model_module, nn.Module):
                model_module.eval()

    def save_model_checkpoint(self,epoch):
        for model_module, module_name, is_external_config in zip(self.models, self.model_module_names, self.is_external_configs):
            if isinstance(model_module, nn.Module):
                unwrapped_model = _unwrap_module(model_module)
                #if model_module._is_frozen():
                if unwrapped_model._is_frozen():
                    print(f'Skipping saving checkpoint for module {module_name} at epoch {epoch}. Module is frozen.')
                    continue
                if is_external_config and (epoch == 0):
                    print(f'Skipping saving checkpoint for external module {module_name} at epoch 0, because weights for this model already exist.')
                    continue
                data_args = {
                    ModelCheckpoint.CONFIG_NAME: self.global_config_name,
                    ModelCheckpoint.EPOCH: epoch,
                    ModelCheckpoint.MODULE: module_name,
                    ModelCheckpoint.DATA: model_module.state_dict()
                }
                if self.data_io.is_file_present(ModelCheckpoint, data_args = data_args):
                    print(f'Skipping saving checkpoint for module {module_name} at epoch {epoch}. Checkpoint already exists.')
                else:
                    self.data_io.save_data(ModelCheckpoint, data_args = data_args)