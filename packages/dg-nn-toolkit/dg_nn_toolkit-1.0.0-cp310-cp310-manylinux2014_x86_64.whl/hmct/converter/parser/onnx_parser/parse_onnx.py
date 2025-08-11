from typing import Union

from horizon_nn.ir import OnnxModel, load_model

from ..registry import register_parse_func


@register_parse_func(model_type="onnx")
def parse_onnx(
    onnx_model_or_proto: Union[
        bytes,
        str,
        "ModelProto",  # noqa: F821
        OnnxModel,
    ],
) -> OnnxModel:
    return load_model(onnx_model_or_proto)
