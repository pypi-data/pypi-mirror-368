import torch

def _unwrap_module(module):
        """
        Unwraps a module if it is wrapped by an accelerator (e.g., DistributedDataParallel).
        """
        if isinstance(module, torch.nn.parallel.DistributedDataParallel):
            return module.module
        return module