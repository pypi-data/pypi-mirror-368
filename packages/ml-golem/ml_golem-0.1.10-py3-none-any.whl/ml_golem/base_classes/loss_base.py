from ml_golem.base_classes.model_base import ModuleAccessingConfigBasedClass

class LossBase(ModuleAccessingConfigBasedClass):
    MAIN_LOSS = 'main_loss'
    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)
        self.batch_loss_dict = {
            self.MAIN_LOSS: []
        }


    def __call__(self, model_input, model_output):
        raise Exception('Not Implemented')
    

    def store_batch_loss(self,loss_results):
        for loss_key in loss_results.keys():
            if loss_key not in self.batch_loss_dict:
                self.batch_loss_dict[loss_key] = []
            self.batch_loss_dict[loss_key].append(loss_results[loss_key].item())

        #self.batch_main_losses.append(loss_results[self.MAIN_LOSS])

    def log_epoch_loss(self, writer, epoch, loss_prefix=''):
        """
        Log the total loss for the epoch to TensorBoard.
        """
        for key in self.batch_loss_dict.keys():
            if len(self.batch_loss_dict[key]) == 0:
                continue
            mean_batch_loss = sum(self.batch_loss_dict[key]) / len(self.batch_loss_dict[key])
            writer.add_scalar(f'{loss_prefix} Loss/{key}', mean_batch_loss, epoch)
            self.batch_loss_dict[key] = [] 