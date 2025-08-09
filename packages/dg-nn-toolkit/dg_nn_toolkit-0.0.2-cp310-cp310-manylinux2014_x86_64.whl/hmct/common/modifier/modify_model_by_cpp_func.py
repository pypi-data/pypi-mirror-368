from typing import Callable

from horizon_nn.ir import OnnxModel, serialize_model


def modify_model_by_cpp_func(
    onnx_model: OnnxModel,
    func: Callable,
    *args,
    **kwargs,
) -> OnnxModel:
    """调用cpp实现的函数修改模型.

    Args:
        onnx_model: 输入待修改的模型
        func: cpp实现的模型修改函数
        *args: 传入到func的位置参数
        **kwargs: 传入到func的关键字参数

    Returns:
        修改后的OnnxModel对象
    """
    onnx_model.reset_proto(func(serialize_model(onnx_model), *args, **kwargs))

    return onnx_model
