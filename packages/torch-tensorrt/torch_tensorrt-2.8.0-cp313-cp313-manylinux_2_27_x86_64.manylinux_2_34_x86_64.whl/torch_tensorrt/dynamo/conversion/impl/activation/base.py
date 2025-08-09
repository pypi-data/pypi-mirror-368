from typing import Any, Callable, Optional

import tensorrt as trt
from torch.fx.node import Target
from torch_tensorrt.dynamo._SourceIR import SourceIR
from torch_tensorrt.dynamo.conversion._ConversionContext import ConversionContext
from torch_tensorrt.fx.converters.converter_utils import (
    mark_as_int8_layer,
    set_layer_name,
)
from torch_tensorrt.fx.types import TRTTensor


def convert_activation(
    ctx: ConversionContext,
    target: Target,
    source_ir: Optional[SourceIR],
    name: str,
    operation_type: trt.ActivationType,
    input_val: TRTTensor,
    alpha: Optional[Any] = None,
    beta: Optional[Any] = None,
    dyn_range_fn: Optional[Callable[[Any], Any]] = None,
) -> TRTTensor:
    """
    Add a TensorRT Activation layer to `network`.
    """
    if not isinstance(input_val, TRTTensor):
        raise RuntimeError(
            f"{operation_type} received input {input_val} that is not part "
            "of the TensorRT region!"
        )
    layer = ctx.net.add_activation(input_val, operation_type)
    if alpha is not None:
        layer.alpha = alpha
    if beta is not None:
        layer.beta = beta
    set_layer_name(layer, target, name, source_ir)

    if (
        not ctx.net.get_flag(trt.NetworkDefinitionCreationFlag.STRONGLY_TYPED)
        and input_val.dynamic_range is not None
        and dyn_range_fn is not None
    ):
        dyn_range = dyn_range_fn(input_val.dynamic_range)
        mark_as_int8_layer(layer, dyn_range)
    return layer.get_output(0)
