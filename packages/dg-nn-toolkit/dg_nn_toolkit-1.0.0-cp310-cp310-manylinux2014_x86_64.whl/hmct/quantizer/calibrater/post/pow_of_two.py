from horizon_nn.ir import OnnxModel

from ..base import CalibrationPass


class PowOfTwo(CalibrationPass):
    def name(self) -> str:
        return "pow_of_two"

    def run_impl(self, calibrated_model: OnnxModel, **kwargs) -> OnnxModel:
        """Updates the quantize_type of HzCalibration nodes to "shift".

        For bernoulli march, quantize_type must only be "shift".
        """
        calibration_nodes = calibrated_model.graph.type2nodes["HzCalibration"]
        for node in calibration_nodes:
            node.quantize_type = "shift"
        return calibrated_model
