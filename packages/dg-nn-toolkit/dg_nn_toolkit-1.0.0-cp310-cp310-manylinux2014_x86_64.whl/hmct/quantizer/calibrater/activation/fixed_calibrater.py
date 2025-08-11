import logging

import numpy as np

from horizon_nn.ir.onnx_model import OnnxModel

from .base import Calibrater


class FixedCalibrater(Calibrater):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.qtype.set_method("fixed")

    @property
    def name(self) -> str:
        return "fixed_calibrater"

    def run_impl(self, calibrated_model: OnnxModel, **kwargs) -> OnnxModel:
        """Run the calibration process using fixed method.

        Args:
            calibrated_model: The calibration model to be used for calibration.
            **kwargs: Other unused parameters.

        Returns:
            The calibrated model with thresholds {1.0} set.
        """
        # 当用户侧未提供校准数据时(check/fast_perf模式),
        # 模型激活节点会采用固定阈值(1.0)。
        logging.info("Run calibration model with fixed thresholds method.")
        calibration_nodes = calibrated_model.graph.type2nodes["HzCalibration"]
        for node in calibration_nodes:
            if node.tensor_type == "feature":
                node.thresholds = np.array([1.0])
        return calibrated_model
