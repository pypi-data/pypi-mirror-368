import torch
from ml_golem.base_classes._helper_functions import _unwrap_module
from ml_golem.base_classes.model_io_base import ModelIOBase

class ModelInference(ModelIOBase):
    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)

        self._prepare_accelerator()

    def __call__(self):
        self._call_core_function_with_autocast(self._inference_core)


    def _inference_core(self):
        with torch.no_grad():  # Disable gradient computation

            if self.dataloader is None:
                results = self.make_forward_pass()
                self.save_inference_results(results)
            else:
                for input_data in self.dataloader:
                    results = self.make_forward_pass(input_data)

                    self.save_inference_results(results,input_data)

            self.complete_inference()

    
    def save_inference_results(self,output,input_data=None):
        # model = self._get_callable_model(-1)
        # if hasattr(model, 'save_results'):
        #     model.save_results(output, input_data)


        model = self.module_order[-1]
        unwrapped_model = _unwrap_module(model)
        if hasattr(unwrapped_model, 'save_results'):
            unwrapped_model.save_results(output, input_data)

    def complete_inference(self):
        # model = self._get_callable_model(-1)
        # if hasattr(model, 'complete_inference'):
        #     model.complete_inference()

        model = self.module_order[-1]
        unwrapped_model = _unwrap_module(model)
        if hasattr(unwrapped_model, 'complete_inference'):
            unwrapped_model.complete_inference()