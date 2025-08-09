import logging
import os
from typing import Dict, Optional, Tuple

import numpy as np

from horizon_nn.common import (
    HbdkDictParser,
    ModelDebugger,
    convert_reshape_target_shape_to_positive,
    infer_shapes,
    prepare_input_data_for_compare,
)
from horizon_nn.executor import ORTExecutor
from horizon_nn.ir import OnnxModel

from .hybrid_build import HybridBuilder
from .required_hbdk import check_hbdk_version


def compile(
    quantized_model: OnnxModel,
    original_model: OnnxModel,
    march: str,
    hbdk_dict_parser: "HbdkDictParser",
    model_debugger: "ModelDebugger",
    batched_input_shapes: Dict,
    name_prefix: str,
) -> Tuple[OnnxModel, HybridBuilder]:
    """Compile onnx model for model convert.

    Returns:
        hybrid onnx model after compilation.
    """
    check_hbdk_version()
    quantized_model = infer_shapes(
        quantized_model, original_model, input_shape=batched_input_shapes
    )

    quantized_model = convert_reshape_target_shape_to_positive(quantized_model)

    output_path = os.path.split(name_prefix)[0]
    hybrid_builder = HybridBuilder(
        quantized_model,
        march,
        hbdk_dict_parser,
        output_path,
        model_debugger.has_debug_method("dump_all_models"),
    )
    hybrid_model = OnnxModel(hybrid_builder.hybrid_model())

    if model_debugger.has_debug_method("check_model_output_consistency"):
        # check consistency between quantized model and hybrid model
        check_quantized_and_hybrid_model(
            quantized_model,
            hybrid_model,
            hbdk_dict_parser.get_input_source(),
        )

    return hybrid_model, hybrid_builder


def check_quantized_and_hybrid_model(
    quantized_model: OnnxModel,
    hybrid_model: OnnxModel,
    input_source: Optional[Dict[str, str]] = None,
):
    """Check consistency between quantized model and hybrid model.

    Args:
        quantized_model: quantized model proto
        hybrid_model: hybrid model proto
        input_source: model input source
    """
    # Create executor.
    quantized_executor = ORTExecutor(quantized_model).to("cpu").create_session()
    hybrid_executor = ORTExecutor(hybrid_model).to("cpu").create_session()
    # Prepare input data.
    quantized_input_data, hybrid_input_data = prepare_input_data_for_compare(
        quantized_model,
        input_source,
    )
    # Get model output
    quantized_output = quantized_executor.forward(quantized_input_data)
    hybrid_output = hybrid_executor.forward(hybrid_input_data)
    # Check model output
    err_msg = (
        "Consistency check between quantized model and "
        + "hybrid model failed as unmatched."
    )
    np.testing.assert_equal(
        len(quantized_output),
        len(quantized_output),
        err_msg + "output count.",
    )
    for name in quantized_output:
        np.testing.assert_array_equal(
            quantized_output[name],
            hybrid_output[name],
            err_msg + "output data.",
        )

    logging.info(
        "The consistency check between the quantized model "
        "and the hybrid model is passed.",
    )
