from typing import Any, Dict, List, Union

from .base import Calibrater
from .fixed_calibrater import FixedCalibrater
from .infer_thresholds import InferThresholds
from .kl_calibrater import KLCalibrater
from .load_calibrater import LoadCalibrater
from .max_calibrater import MaxCalibrater
from .min_max_calibrater import MinMaxCalibrater
from .mix_calibrater import MixCalibrater
from ..calibration_method import CalibrationMethod


def activation_calibration(
    activation_config: Dict[str, Any],
    modelwise_search: Dict[str, Any],
    layerwise_search: Dict[str, Any],
) -> Union[Calibrater, List[Calibrater]]:
    act_types = activation_config.get("calibration_type")
    if not isinstance(act_types, list):
        act_types = [act_types]

    if len(act_types) == 1 and act_types[0] == "fixed":
        return FixedCalibrater()
    if len(act_types) == 1 and act_types[0] == "load":
        return LoadCalibrater()
    if (len(act_types) == 1 and act_types[0] == "mix") or layerwise_search:
        return MixCalibrater(layerwise_search)
    if len(act_types) == 1 and act_types[0] == "min-max":
        return MinMaxCalibrater()

    act_passes = []
    for act_type in act_types:
        if act_type == "kl":
            act_passes.append(KLCalibrater(activation_config))
        if act_type == "max":
            act_passes.append(MaxCalibrater(activation_config))
    calibration_methods = CalibrationMethod()
    for act_pass in act_passes:
        calibration_methods += act_pass.calibration_methods
    act_passes.append(InferThresholds(calibration_methods, modelwise_search))
    return act_passes
