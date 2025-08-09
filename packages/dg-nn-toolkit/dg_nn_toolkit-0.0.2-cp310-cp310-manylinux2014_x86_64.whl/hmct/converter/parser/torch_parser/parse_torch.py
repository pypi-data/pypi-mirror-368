import io
from typing import Mapping, Optional, Sequence, Tuple, Union

import torch

from horizon_nn.ir import OnnxModel

from .export_onnx import export_onnx
from ..registry import register_parse_func


@register_parse_func(model_type="torch")
def parse_torch(
    model: torch.nn.Module,
    dummy_inputs: Union[Tuple, torch.Tensor],
    input_names: Optional[Sequence[str]] = None,
    output_names: Optional[Sequence[str]] = None,
    opset_version: int = 11,
    dynamic_axes: Optional[
        Union[Mapping[str, Mapping[int, str]], Mapping[str, Sequence[int]]]
    ] = None,
) -> OnnxModel:
    f = io.BytesIo()
    export_onnx(
        model=model,
        dummy_inputs=dummy_inputs,
        onnx_file=f,
        input_names=input_names,
        output_names=output_names,
        opset_version=opset_version,
        dynamic_axes=dynamic_axes,
    )
    return OnnxModel(f.getvalue())
