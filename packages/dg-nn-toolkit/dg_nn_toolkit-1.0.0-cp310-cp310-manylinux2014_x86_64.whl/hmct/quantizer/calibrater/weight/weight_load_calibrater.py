import logging

import numpy as np

from horizon_nn.ir import OnnxModel

from .utils import check_and_obtain_group_attribute
from ..base import CalibrationPass


class WeightLoadCalibrater(CalibrationPass):
    @property
    def name(self) -> str:
        return "weight_load_calibrater"

    def run_impl(self, calibrated_model: OnnxModel, **kwargs) -> OnnxModel:
        """基于load校准的模型权重阈值计算.

        load校准下输入模型为QAT模型, 因此仅对阈值缺失的校准节点做阈值计算,
        模型已有的阈值依然保留

        Args:
            calibrated_model: 模型权重待校准的模型(已插入校准节点)
            **kwargs: 其他未被使用到的传入参数

        Returns:
            模型权重完成校准的模型
        """
        logging.info("Run calibration model with load threshold method for weight.")
        calibration_nodes = calibrated_model.graph.type2nodes["HzCalibration"]
        for node in calibration_nodes:
            if node.tensor_type == "weight":
                param_value = node.inputs[0].value
                param_shape = node.inputs[0].shape
                next_op_types = {next_op.op_type for next_op in node.next_ops}
                if next_op_types.issubset({"Conv", "HzPreprocess"}):
                    group = check_and_obtain_group_attribute(node)
                    node.group = group
                    if node.thresholds is None:
                        node.axis = 0
                        node.thresholds = self.calibrate_channel_thresholds(
                            param_value, 0
                        )
                        node.constant = 1
                elif next_op_types.issubset({"ConvTranspose"}):
                    group = check_and_obtain_group_attribute(node)
                    node.group = group
                    if node.thresholds is None:
                        node.axis = 1
                        param_value = param_value.reshape(
                            group,
                            param_shape[0] // group,
                            *param_shape[1:],
                        )
                        param_value = np.swapaxes(param_value, axis1=1, axis2=2)
                        param_value = param_value.reshape(
                            param_shape[1] * group,
                            param_shape[0] // group,
                            *param_shape[2:],
                        )
                        node.thresholds = self.calibrate_channel_thresholds(
                            param_value, 0
                        )
                        node.constant = 1
        return calibrated_model

    def calibrate_channel_thresholds(
        self,
        param_value: np.ndarray,
        axis: int,
    ) -> np.ndarray:
        assert isinstance(param_value, np.ndarray), (
            "type(param_value) should be np.ndarray, " + f"but got {type(param_value)}."
        )
        assert param_value.ndim > axis, (
            "channel axis should be less then " + f"{param_value.ndim}, but got {axis}."
        )
        return (
            abs(param_value)
            .max(
                tuple(_ for _ in range(param_value.ndim) if _ != axis),
            )
            .clip(np.finfo(np.float32).tiny, np.finfo(np.float32).max)
        )

    def calibrate_tensor_thresholds(self, param_value: np.ndarray) -> np.ndarray:
        assert isinstance(param_value, np.ndarray), (
            "type(param_value) should be np.ndarray, " + f"but got {type(param_value)}."
        )
        return np.array(
            [
                abs(param_value)
                .max()
                .clip(np.finfo(np.float32).tiny, np.finfo(np.float32).max),
            ],
        )
