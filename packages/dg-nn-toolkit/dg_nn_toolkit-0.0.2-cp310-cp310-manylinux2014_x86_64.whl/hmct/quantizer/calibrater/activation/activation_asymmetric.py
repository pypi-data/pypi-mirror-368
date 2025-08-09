from horizon_nn.common import modify_model_by_cpp_func
from horizon_nn.ir import OnnxModel
from horizon_nn.ir.horizon_onnx import global_attributes, quantizer

from ..base import CalibrationPass
from ..quantization_type import QuantizationType


class ActivationAsymmetric(CalibrationPass):
    def __init__(self):
        """Initialize the ConvertAsymq pass with the specified asymmetric mode."""
        global_attributes.set_asymmetric_mode("disable_dw_pad")
        self.qtype = QuantizationType()
        self.qtype.asymmetric = True

    @property
    def name(self) -> str:
        return "activation_asymmetric"

    def run_impl(self, calibrated_model: OnnxModel, **kwargs) -> OnnxModel:
        calibrated_model = modify_model_by_cpp_func(
            calibrated_model, quantizer.convert_symq_to_asymq
        )
        calibration_nodes = calibrated_model.graph.type2nodes["HzCalibration"]
        for node in calibration_nodes:
            if node.qtype in {"uint8"}:
                node.support_asymq = True
        return calibrated_model
