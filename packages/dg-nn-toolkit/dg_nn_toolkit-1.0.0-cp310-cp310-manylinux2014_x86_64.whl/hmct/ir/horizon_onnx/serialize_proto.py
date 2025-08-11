import os
import time
from typing import Union

from onnx import ModelProto, load, load_from_string, save

from horizon_nn.utility import TEMP_DIR

LARGEST_NO_EXTERNAL_DATA_MODEL = 2**31 - 1


def serialize_proto(onnx_proto: ModelProto) -> Union[str, bytes]:
    """从ModelProto解析模型.

    若模型小于2GB则使用protobuf解析成字节流

    若模型大于2GB则使用临时文件夹存储模型并返回地址

    """
    if onnx_proto.ByteSize() < LARGEST_NO_EXTERNAL_DATA_MODEL:
        model_str = onnx_proto.SerializeToString()
    else:
        model_str = TEMP_DIR.relpath(f"temp.{int(time.time())}.onnx")
        save(
            onnx_proto,
            model_str,
            save_as_external_data=True,
        )
    return model_str


def deserialize_proto(model_str: Union[str, bytes]) -> ModelProto:
    """从传入的string类型或者bytes类型对象重新构建出ModelProto对象并返回."""
    if isinstance(model_str, bytes):
        model_proto = load_from_string(model_str)
    else:
        if os.path.isfile(model_str):
            model_proto = load(model_str)
        else:
            raise TypeError(
                f"model_proto should be valid filepath,but got: {model_str}."
            )
    return model_proto
