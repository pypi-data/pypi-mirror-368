from typing import Any, Sequence

import numpy as np

from horizon_nn.ir.onnx_utils import TensorProto, mapping


def make_string_tensor(
    name: str,
    data_type: int,
    dims: Sequence[int],
    vals: Any,
) -> TensorProto:
    assert (
        data_type == TensorProto.STRING
    ), f"Expect data_type to be STRING, but got {data_type}"
    tensor = TensorProto()
    tensor.data_type = data_type
    tensor.name = name

    if type(vals) is np.ndarray and len(vals.shape) > 1:
        vals = vals.flatten()

    field = mapping.STORAGE_TENSOR_TYPE_TO_FIELD[
        mapping.TENSOR_TYPE_TO_STORAGE_TENSOR_TYPE[data_type]
    ]

    getattr(tensor, field).extend(vals)
    tensor.dims.extend(dims)

    return tensor
