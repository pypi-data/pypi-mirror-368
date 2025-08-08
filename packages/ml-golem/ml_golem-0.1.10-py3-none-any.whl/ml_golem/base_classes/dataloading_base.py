import torch
import itertools
from ml_golem.model_loading_logic.config_based_class import ConfigBasedClass
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from torch.utils.data import DataLoader
from ml_golem.base_classes.dataset_base import DatasetBase
from ml_golem.base_classes.loss_base import LossBase
            
class DataIterationBase(ConfigBasedClass):

    def _initialize_dataloader(self,args,subconfig_keys):
        config = self.data_io.fetch_subconfig(
            self.global_config_name,
            subconfig_keys=subconfig_keys)

        if ModelConfigKeywords.DATASET.value not in config:
            return None
            
        dataset = self.instantiate_config_based_class(
            args,
            self.global_config_name,
            subconfig_keys=subconfig_keys+[ModelConfigKeywords.DATASET.value],
            default_class=DatasetBase)
        
        dataset._set_module_names_and_pointers(
            module_names=self.model_module_names,
            models=self.models)
        


        dataloader_config= self.data_io.fetch_subconfig(
            self.global_config_name,
            subconfig_keys=subconfig_keys+[ModelConfigKeywords.DATALOADER.value])
        
        dataloader = DataLoader(dataset,
            batch_size=dataloader_config.get(ModelConfigKeywords.BATCH_SIZE.value, 1), 
            num_workers=dataloader_config.get(ModelConfigKeywords.NUM_WORKERS.value,0),
            collate_fn=dataset._get_custom_collate_fn(),
            shuffle=dataloader_config.get(ModelConfigKeywords.CAN_SHUFFLE.value, self._can_shuffle()), 
            pin_memory=True)
        return dataloader

    def _initialize_loss(self,args,subconfig_keys):
        loss = self.instantiate_config_based_class(
            args,
            self.global_config_name,
            subconfig_keys=subconfig_keys+[ModelConfigKeywords.LOSS.value],
            default_class=LossBase)
        
        loss._set_module_names_and_pointers(
            module_names=self.model_module_names,
            models=self.models)
        

        return loss
    
    def _initialize_optimizer(self):
        self.weight_decay = self.data_io.fetch_config_field(
            self.config,
            subconfig_keys=[ModelConfigKeywords.LOSS.value, ModelConfigKeywords.WEIGHT_DECAY.value],
            default=0.0
        )

        self.learning_rate = float(self.config[ModelConfigKeywords.LEARNING_RATE.value])





        # Combine parameters from all models
        #combined_parameters = itertools.chain(*[model.parameters() for model in self.models])
        combined_parameters = itertools.chain(*[model.parameters() for model in self.models if isinstance(model, torch.nn.Module)])
        optimizer = torch.optim.Adam(
            combined_parameters, 
            lr=self.learning_rate,
            weight_decay=self.weight_decay)
        
        return optimizer

    
    def _can_shuffle(self):
        return False