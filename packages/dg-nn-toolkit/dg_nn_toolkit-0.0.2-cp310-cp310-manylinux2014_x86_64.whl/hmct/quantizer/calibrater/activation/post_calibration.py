from horizon_nn.common import modify_model_by_cpp_func
from horizon_nn.ir import OnnxModel
from horizon_nn.ir.horizon_onnx import quantizer

from ..base import CalibrationPass
from ..utils import convert_to_ptq_model


class PostCalibration(CalibrationPass):
    @property
    def name(self) -> str:
        return "post_calibration"

    def run_impl(self, calibrated_model: OnnxModel, **kwargs) -> OnnxModel:
        """Create post calibrated model from calibrated model.

        The post calibration includes various modifications such as
        complement calibration node, adjust threshold.
        """
        post_calibrated_model = modify_model_by_cpp_func(
            calibrated_model,
            quantizer.create_post_calibrated_model,
        )
        post_calibrated_model = convert_to_ptq_model(post_calibrated_model)
        post_calibrated_model.check_validity()

        return post_calibrated_model
