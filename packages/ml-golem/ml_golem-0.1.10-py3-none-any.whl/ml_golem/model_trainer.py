import torch
from tqdm import tqdm
from torch.utils.tensorboard import SummaryWriter
from ml_golem.base_classes.model_io_base import ModelIOBase,ModelConfigKeywords
from ml_golem.datatypes import TrainingLog
from ml_golem.base_classes._timer import Timer

class ModelTrainer(ModelIOBase):
    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)


        self.loss = self._initialize_loss(args,subconfig_keys)
        self.optimizer = self._initialize_optimizer()
        
        self.save_every = self.config[ModelConfigKeywords.SAVE_EVERY.value]

        #TODO: Improve the logic to have validation inherent from training, unless overrides are specified.
        self.validate_every = self.config.get(ModelConfigKeywords.VALIDATE_EVERY.value, -1)
        if self.validate_every > 0:
            self.validation_dataloader = self._initialize_dataloader(args,subconfig_keys+[ModelConfigKeywords.VALIDATION.value])
            self.validation_loss = self._initialize_loss(args,subconfig_keys+[ModelConfigKeywords.VALIDATION.value])

        self._prepare_accelerator()
        

        #TODO: DIG DEEPER INTO using .add_hparams to store relevant hyperparameters on grid searches
        #It seems as if h params cannot be shown in in the time series training window, only in its own hparams window. This is rather annoying.

        self.log_dir = self.data_io.get_data_path(TrainingLog, data_args={
            TrainingLog.CONFIG_NAME: self.global_config_name,
        })

        self.writer = SummaryWriter(self.log_dir)

        self.epochs = self.config[ModelConfigKeywords.EPOCHS.value]
        self.can_display_epoch_progress = self.config.get(ModelConfigKeywords.CAN_DISPLAY_EPOCH_PROGRESS.value, True)
        self.can_time_batch = self.config.get(ModelConfigKeywords.CAN_TIME_BATCH.value, False)
        if self.can_time_batch:
            self.timer = Timer()
            self._batch_size = self.data_io.fetch_subconfig(self.global_config_name,
                subconfig_keys=subconfig_keys+[ModelConfigKeywords.DATALOADER.value]).get(ModelConfigKeywords.BATCH_SIZE.value, 1)


    def __call__(self):
        self._call_core_function_with_autocast(self._train_core)


    def _train_core(self):
        self.switch_model_to_train()  # Switch back to training mode
        epoch_iterator = range(self.resume_epoch, self.epochs)
        if self.can_display_epoch_progress:
            epoch_iterator = tqdm(epoch_iterator, desc="Epochs")
        for epoch in epoch_iterator:
            self._check_epoch_to_save_or_validate(epoch)
            for input_batch in self.dataloader:
                if self.can_time_batch:
                    self.timer.start()
                self.optimizer.zero_grad()
                output_batch = self.make_forward_pass(input_batch)
                loss_results = self.loss(input_batch,output_batch)
                self.accelerator.backward(loss_results[self.loss.MAIN_LOSS])
                self.optimizer.step()
                self.loss.store_batch_loss(loss_results)
                if self.can_time_batch:
                    elapsed_time = self.timer.stop()
                    predicted_epoch_time = elapsed_time * len(self.dataloader) / (self._batch_size)
                    print(f'Batch time: {self.timer.format_time(elapsed_time)}. Predicted epoch time: {self.timer.format_time(predicted_epoch_time)}')
            self.loss.log_epoch_loss(self.writer,epoch,loss_prefix='train_')
            self._update_log_permissions()
        self._check_epoch_to_save_or_validate(self.epochs)
        self.writer.close() #Might be necessary to close the writer to ensure all data is flushed to disk.


    def _update_log_permissions(self):
        self.data_io._extend_group_permissions(self.log_dir,datatype=TrainingLog)

    def _can_shuffle(self):
        return True
    
    def _check_epoch_to_save_or_validate(self,epoch):
        if self.save_every > 0:
            if (epoch % self.save_every == 0) or (epoch == self.epochs):
                self.save_model_on_epoch(epoch)

        if self.validate_every > 0:
            if (epoch % self.validate_every == 0) or (epoch == self.epochs):
                self.validate_on_epoch(epoch)

    def validate_on_epoch(self, epoch):
        print(f'Validating on epoch {epoch}')
        self.switch_model_to_eval()  # Switch to evaluation mode
        with torch.no_grad():  # Disable gradient computation
            for input_batch in self.validation_dataloader:
                output_batch = self.make_forward_pass(input_batch)
                loss_results = self.validation_loss(input_batch, output_batch)
                self.validation_loss.store_batch_loss(loss_results)
            self.validation_loss.log_epoch_loss(self.writer,epoch,loss_prefix='validate_')

        self.switch_model_to_train()  # Switch back to training mode
        print(f'Validation of epoch {epoch} complete')


    def save_model_on_epoch(self, epoch):
        if self.accelerator.is_main_process:
            self.save_model_checkpoint(epoch)
        self.accelerator.wait_for_everyone()