from typing import Dict, List, Optional, Union

import numpy as np

from horizon_nn.ir import OnnxModel, onnx_dtype_to_numpy_dtype


def random_data(
    shape: List[int],
    dtype: np.dtype = np.float32,
    range: Optional[List[Union[int, float]]] = None,
):
    """生成随机数据."""
    if range is not None:
        assert len(range) == 2
    if dtype in (np.float32, np.float64):
        # 浮点数据范围太大, 暂时使用一个较小范围
        range = [-1.0, 1.0] if range is None else range
        data = np.random.uniform(range[0], range[1], shape).astype(dtype)
    elif dtype in (np.int8, np.uint8, np.int16, np.uint16, np.int32, np.int64):
        # 为了避免Gather等算子的indices超出限制, 这里range默认使用[-1, 2)
        range = [-1, 2] if range is None else range
        data = np.random.randint(range[0], range[1], shape).astype(dtype)
    elif dtype == bool:
        data = np.random.randint(0, 2, shape).astype(bool)
    else:
        raise ValueError("Unsupported data type is given: " + str(dtype))
    return data


def random_yuv444_nv12_data(input_shape: List[int], input_source: Dict[str, str]):
    idx_c = 3
    if len(input_shape) != 4 or input_shape[idx_c] not in [1, 3]:
        raise ValueError("For pyramid input, channel must be 1 or 3.")
    # yuv444_128 for quantized, nv12 for hybrid
    nv12_data = random_data(input_shape, np.uint8, [0, 255])
    if input_shape[idx_c] == 3:
        nv12_data[:, 0::2, 1::2, 1:] = nv12_data[:, 0::2, 0:-1:2, 1:]
        nv12_data[:, 1::2, 0::2, 1:] = nv12_data[:, 0:-1:2, 0::2, 1:]
        nv12_data[:, 1::2, 1::2, 1:] = nv12_data[:, 0:-1:2, 0:-1:2, 1:]
    yuv444_data = (nv12_data - 128).astype(np.int8)
    return yuv444_data, nv12_data.astype(np.int8)


def prepare_input_data_for_compare(
    model: OnnxModel, input_source: Optional[Dict[str, str]] = None
):
    """为quantized模型和hybrid模型提供一致性比较所需的输入数据."""
    quantized_data = {}
    hybrid_data = {}
    for i in model.graph.inputs:
        dtype = onnx_dtype_to_numpy_dtype(i.dtype)
        if (
            dtype == np.int8
            and input_source is not None
            and input_source.get(i.name, "ddr") == "pyramid"
        ):
            yuv444_data, nv12_data = random_yuv444_nv12_data(i.shape, input_source)
            quantized_data[i.name] = yuv444_data
            hybrid_data[i.name] = nv12_data
        else:
            input_data = random_data(i.shape, dtype)
            quantized_data[i.name] = input_data
            hybrid_data[i.name] = input_data
    return quantized_data, hybrid_data
