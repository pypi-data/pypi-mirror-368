import io
from typing import Mapping, Optional, Sequence, Tuple, Union

import torch

from .register_custom_op import *  # noqa: F403


def export_onnx(
    model: torch.nn.Module,
    dummy_inputs: Union[Tuple, torch.Tensor],
    onnx_file: Union[str, io.BytesIO],
    input_names: Optional[Sequence[str]] = None,
    output_names: Optional[Sequence[str]] = None,
    opset_version: int = 11,
    dynamic_axes: Optional[
        Union[Mapping[str, Mapping[int, str]], Mapping[str, Sequence[int]]]
    ] = None,
    **kwargs,
) -> None:
    """将torch模型(torch.nn.Module)导出成onnx模型(ModelProto).

    Args:
        model: 用于导出的torch模型
        dummy_inputs: torch模型输入, 用于完成模型tracing
        onnx_file: 用于保存导出onnx模型的路径名或者字节流对象
        input_names: 导出onnx模型的输入名称序列
        output_names: 导出onnx模型的输出名称序列
        opset_version: 导出onnx模型的opset版本
        dynamic_axes: 导出onnx模型输入和输出的动态维度
        **kwargs: 其他公版torch导出onnx模型所需参数
    """
    assert isinstance(
        model,
        torch.nn.Module,
    ), "The input model is not of type torch.nn.Module."
    model.eval()
    torch.onnx.export(
        model,
        dummy_inputs,
        onnx_file,
        input_names=input_names,
        output_names=output_names,
        opset_version=opset_version,
        dynamic_axes=dynamic_axes,
        **kwargs,
    )
