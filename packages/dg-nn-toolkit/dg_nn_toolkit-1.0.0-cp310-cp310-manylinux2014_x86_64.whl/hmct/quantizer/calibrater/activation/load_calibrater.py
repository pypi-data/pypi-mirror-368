import logging

from horizon_nn.ir import OnnxModel

from .base import Calibrater


class LoadCalibrater(Calibrater):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.qtype.set_method("load")

    @property
    def name(self) -> str:
        return "load_calibrater"

    def run_impl(self, calibrated_model: OnnxModel, **kwargs) -> OnnxModel:
        """Run the calibration model using the load method for activation.

        Args:
            calibrated_model: The calibrated model to be used for calibration.
            **kwargs: Other unused parameters.

        Returns:
            The calibrated model with activation thresholds set.
        """
        logging.info("Run calibration model with load threshold method for activation.")
        return calibrated_model
