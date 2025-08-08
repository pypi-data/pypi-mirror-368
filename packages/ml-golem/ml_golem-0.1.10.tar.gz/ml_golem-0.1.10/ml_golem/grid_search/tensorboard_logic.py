from ml_golem.base_classes.data_io_object import DataIOObject
from ml_golem.datatypes import TrainingLog

class TensorBoardLogic(DataIOObject):
    def __init__(self,args):
        super().__init__(args)
        self.global_config_name = args.config_name


    def __call__(self):
        tensorboard_path = self.data_io.get_data_path(TrainingLog,data_args ={
            TrainingLog.CONFIG_NAME: self.global_config_name
        })
        tensorboard_command = (
            'tensorboard '
            f'--logdir {tensorboard_path}'
        )
        self.data_io.run_system_command(tensorboard_command)
