
from gguf_connector.quant2c import dequantize_functions
from gguf_connector.reader import GGML_QUANT_SIZES
# call gguf-connector engine striaght for easier maintenance

import torch
import torch.nn as nn
import inspect
from contextlib import nullcontext

from ...utils import is_accelerate_available
# credits should be given to huggingface and city96 for this part still

if is_accelerate_available():
    import accelerate
    from accelerate import init_empty_weights
    from accelerate.hooks import add_hook_to_module, remove_hook_from_module

# Copied from diffusers.quantizers.bitsandbytes.utils._create_accelerate_new_hook
def _create_accelerate_new_hook(old_hook):
    r"""
    Creates a new hook based on the old hook. Use it only if you know what you are doing ! This method is a copy of:
    https://github.com/huggingface/peft/blob/748f7968f3a31ec06a1c2b0328993319ad9a150a/src/peft/utils/other.py#L245 with
    some changes
    """
    old_hook_cls = getattr(accelerate.hooks, old_hook.__class__.__name__)
    old_hook_attr = old_hook.__dict__
    filtered_old_hook_attr = {}
    old_hook_init_signature = inspect.signature(old_hook_cls.__init__)
    for k in old_hook_attr.keys():
        if k in old_hook_init_signature.parameters:
            filtered_old_hook_attr[k] = old_hook_attr[k]
    new_hook = old_hook_cls(**filtered_old_hook_attr)
    return new_hook

def _replace_with_gguf_linear(model, compute_dtype, state_dict, prefix="", modules_to_not_convert=[]):
    def _should_convert_to_gguf(state_dict, prefix):
        weight_key = prefix + "weight"
        return weight_key in state_dict and isinstance(state_dict[weight_key], GGUFParameter)

    has_children = list(model.children())
    if not has_children:
        return

    for name, module in model.named_children():
        module_prefix = prefix + name + "."
        _replace_with_gguf_linear(module, compute_dtype, state_dict, module_prefix, modules_to_not_convert)

        if (
            isinstance(module, nn.Linear)
            and _should_convert_to_gguf(state_dict, module_prefix)
            and name not in modules_to_not_convert
        ):
            ctx = init_empty_weights if is_accelerate_available() else nullcontext
            with ctx():
                model._modules[name] = GGUFLinear(
                    module.in_features,
                    module.out_features,
                    module.bias is not None,
                    compute_dtype=compute_dtype,
                )
            model._modules[name].source_cls = type(module)
            # Force requires_grad to False to avoid unexpected errors
            model._modules[name].requires_grad_(False)
    return model

def _dequantize_gguf_and_restore_linear(model, modules_to_not_convert=[]):
    for name, module in model.named_children():
        if isinstance(module, GGUFLinear) and name not in modules_to_not_convert:
            device = module.weight.device
            bias = getattr(module, "bias", None)

            ctx = init_empty_weights if is_accelerate_available() else nullcontext
            with ctx():
                new_module = nn.Linear(
                    module.in_features,
                    module.out_features,
                    module.bias is not None,
                    device=device,
                )
            new_module.weight = nn.Parameter(dequantize_gguf_tensor(module.weight))
            if bias is not None:
                new_module.bias = bias

            # Create a new hook and attach it in case we use accelerate
            if hasattr(module, "_hf_hook"):
                old_hook = module._hf_hook
                new_hook = _create_accelerate_new_hook(old_hook)

                remove_hook_from_module(module)
                add_hook_to_module(new_module, new_hook)

            new_module.to(device)
            model._modules[name] = new_module

        has_children = list(module.children())
        if has_children:
            _dequantize_gguf_and_restore_linear(module, modules_to_not_convert)

    return model

SUPPORTED_GGUF_QUANT_TYPES = list(dequantize_functions.keys())

def _quant_shape_from_byte_shape(shape, type_size, block_size):
    return (*shape[:-1], shape[-1] // type_size * block_size)

def dequantize_gguf_tensor(tensor):
    if not hasattr(tensor, "quant_type"):
        return tensor

    quant_type = tensor.quant_type
    dequant_fn = dequantize_functions[quant_type]

    block_size, type_size = GGML_QUANT_SIZES[quant_type]

    tensor = tensor.view(torch.uint8)
    shape = _quant_shape_from_byte_shape(tensor.shape, type_size, block_size)

    n_blocks = tensor.numel() // type_size
    blocks = tensor.reshape((n_blocks, type_size))

    dequant = dequant_fn(blocks, block_size, type_size)
    dequant = dequant.reshape(shape)

    return dequant.as_tensor()

class GGUFParameter(torch.nn.Parameter):
    def __new__(cls, data, requires_grad=False, quant_type=None):
        data = data if data is not None else torch.empty(0)
        self = torch.Tensor._make_subclass(cls, data, requires_grad)
        self.quant_type = quant_type
        block_size, type_size = GGML_QUANT_SIZES[quant_type]
        self.quant_shape = _quant_shape_from_byte_shape(self.shape, type_size, block_size)
        return self

    def as_tensor(self):
        return torch.Tensor._make_subclass(torch.Tensor, self, self.requires_grad)

    @staticmethod
    def _extract_quant_type(args):
        # When converting from original format checkpoints we often use splits, cats etc on tensors
        # this method ensures that the returned tensor type from those operations remains GGUFParameter
        # so that we preserve quant_type information
        for arg in args:
            if isinstance(arg, list) and isinstance(arg[0], GGUFParameter):
                return arg[0].quant_type
            if isinstance(arg, GGUFParameter):
                return arg.quant_type
        return None

    @classmethod
    def __torch_function__(cls, func, types, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}

        result = super().__torch_function__(func, types, args, kwargs)

        if isinstance(result, torch.Tensor):
            quant_type = cls._extract_quant_type(args)
            return cls(result, quant_type=quant_type)
        # Handle tuples and lists
        elif type(result) in (list, tuple):
            # Preserve the original type (tuple or list)
            quant_type = cls._extract_quant_type(args)
            wrapped = [cls(x, quant_type=quant_type) if isinstance(x, torch.Tensor) else x for x in result]
            return type(result)(wrapped)
        else:
            return result

class GGUFLinear(nn.Linear):
    def __init__(
        self,
        in_features,
        out_features,
        bias=False,
        compute_dtype=None,
        device=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device)
        self.compute_dtype = compute_dtype

    def forward(self, inputs):
        weight = dequantize_gguf_tensor(self.weight)
        weight = weight.to(self.compute_dtype)
        bias = self.bias.to(self.compute_dtype) if self.bias is not None else None

        output = torch.nn.functional.linear(inputs, weight, bias)
        return output