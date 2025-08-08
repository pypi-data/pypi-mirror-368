from ml_golem.model_loading_logic.config_based_class import ConfigBasedClass
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from ml_golem.datatypes import ModelCheckpoint, TrainingLog
from file_golem import FilePathEntries
from ml_golem.model_inference import ModelInference
from ml_golem.model_trainer import ModelTrainer

class ModelAction(ConfigBasedClass):
    def train(self,args):
        print(f'Training: {self.global_config_name}')
        trainer = self.instantiate_config_based_class(
            args,
            self.global_config_name,
            subconfig_keys = [ModelConfigKeywords.TRAINING.value],
            default_class=ModelTrainer)
        trainer()

    def inference(self,args):
        print(f'Inference: {self.global_config_name}')
        inference = self.instantiate_config_based_class(
            args,
            self.global_config_name,
            subconfig_keys = [ModelConfigKeywords.INFERENCE.value],
            default_class=ModelInference)
        inference()

    def wipe(self):
        print(f'Wipe: {self.global_config_name}')
        print('WARNING: YOU PROBABLY DONT WANT TO CALL WIPE')
        self.data_io.delete_data(ModelCheckpoint,data_args = {
            ModelCheckpoint.CONFIG_NAME: self.global_config_name,
            ModelCheckpoint.EPOCH:FilePathEntries.OPEN_ENTRY
        })

        self.data_io.delete_data(ModelCheckpoint,data_args = {
            ModelCheckpoint.CONFIG_NAME: self.global_config_name,
            ModelCheckpoint.EPOCH:FilePathEntries.OPEN_ENTRY,
            ModelCheckpoint.MODULE: FilePathEntries.OPEN_ENTRY
        })

        self.data_io.delete_data(TrainingLog,data_args = {
            TrainingLog.CONFIG_NAME: self.global_config_name,
        })