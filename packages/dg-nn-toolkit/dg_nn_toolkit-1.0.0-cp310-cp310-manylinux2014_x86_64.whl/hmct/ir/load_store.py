import os
from typing import Union

from .horizon_onnx.serialize_proto import (
    LARGEST_NO_EXTERNAL_DATA_MODEL,
    deserialize_proto,
    serialize_proto,
)
from .onnx_model import OnnxModel
from .onnx_utils import ModelProto
from .onnx_utils import save_model as save_proto


def load_model(
    onnx_model_or_proto: Union[bytes, str, ModelProto, OnnxModel],
) -> OnnxModel:
    """加载不同格式onnx模型并统一解析成OnnxModel对象."""
    if isinstance(onnx_model_or_proto, OnnxModel):
        onnx_model = onnx_model_or_proto
    elif isinstance(onnx_model_or_proto, (bytes, str, ModelProto)):
        onnx_model = OnnxModel(onnx_model_or_proto)
    else:
        raise ValueError(
            f"type(onnx_model_or_proto) should be one of OnnxModel, bytes, str, "
            f"and ModelProto, but got {type(onnx_model_or_proto)}",
        )

    return _compatibility(onnx_model)


def save_model(
    onnx_model_or_proto: Union[ModelProto, bytes, OnnxModel],
    onnx_file: str,
) -> None:
    """将不同格式onnx模型保存到指定的文件."""
    if isinstance(onnx_model_or_proto, (bytes, ModelProto)):
        onnx_proto = onnx_model_or_proto
    elif isinstance(onnx_model_or_proto, OnnxModel):
        onnx_proto = onnx_model_or_proto.proto
    else:
        raise ValueError(
            f"type(onnx_model_or_proto) should be one of bytes, ModelProto "
            f"and OnnxModel, but got {type(onnx_model_or_proto)}",
        )
    if (
        isinstance(onnx_proto, ModelProto)
        and onnx_proto.ByteSize() > LARGEST_NO_EXTERNAL_DATA_MODEL
    ):
        external_data_path = os.path.basename(onnx_file) + ".data"
        if os.path.exists(external_data_path):
            os.remove(external_data_path)
        save_proto(
            onnx_proto,
            onnx_file,
            save_as_external_data=True,
            all_tensors_to_one_file=True,
            location=external_data_path,
        )
    else:
        save_proto(proto=onnx_proto, f=onnx_file)


def serialize_model(onnx_model: OnnxModel) -> Union[str, bytes]:
    """对OnnxModel对象序列化.

    小于2GB的模型返回序列化后的字节流;

    大于2GB的模型将存储在临时文件夹中并返回文件地址.

    """
    model_proto = onnx_model.proto
    return serialize_proto(model_proto)


def deserialize_model(model_str: Union[str, bytes]) -> OnnxModel:
    """将包含序列化模型的字节流转换成相应的OnnxModel对象.

    或从存储模型的临时文件夹地址获取OnnxModel对象.
    """
    model_proto = deserialize_proto(model_str)
    return OnnxModel(model_proto)


def _compatibility(onnx_model: OnnxModel) -> OnnxModel:
    for onnx_node in onnx_model.graph.nodes:
        if onnx_node.op_type.startswith("Hz"):
            onnx_node.domain = "horizon"

    return onnx_model
