from horizon_nn.ir import OnnxModel

from .registry import PARSE_FUNC_REGISTRY


def parse(model_type: str, *args, **kwargs) -> OnnxModel:
    # call the corresponding parse func based on model type
    return PARSE_FUNC_REGISTRY[model_type](*args, **kwargs)
