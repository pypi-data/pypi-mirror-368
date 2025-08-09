from horizon_nn.common import constant_folding, modify_model_by_cpp_func
from horizon_nn.ir import OnnxModel
from horizon_nn.ir.horizon_onnx import quantizer


def optimize(original_model: OnnxModel) -> OnnxModel:
    optimized_model = constant_folding(original_model)
    optimized_model = modify_model_by_cpp_func(
        onnx_model=optimized_model, func=quantizer.optimize
    )

    return optimized_model  # noqa: RET504
