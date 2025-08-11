from abc import abstractmethod
from typing import Container, Iterable, Iterator, List, Union

from horizon_nn.common import PassBase
from horizon_nn.ir import OnnxModel


class CalibrationPass(PassBase):
    """CalibrationPass defines common interfaces for different calibration passes.

    This class provides a template for implementing the specific
    calibration pass.
    """

    @abstractmethod
    def run_impl(self, calibrated_model: OnnxModel, **kwargs) -> OnnxModel:
        raise NotImplementedError("run_impl Not Implemented for CalibrationPass.")


class CalibrationPipeline(Container, Iterable):
    """CalibrationPipeline stores a list of CalibrationPass.

    It provides methods to add calibration passes to the pipeline,
    calibrate a model using the pipeline, and iterate over the calibration
    passes in the pipeline.
    """

    def __init__(self):
        super().__init__()
        self._pipelines = []

    def set(self, passes: Union[List[CalibrationPass], CalibrationPass]) -> None:
        if isinstance(passes, CalibrationPass):
            passes = [passes]
        for cal_pass in passes:
            assert isinstance(cal_pass, CalibrationPass), (
                "Calibration Pipeline only suppose to contain calibration "
                f"passes, but got {cal_pass!s}({type(cal_pass)})."
            )
        self._pipelines.extend(passes)

    def calibrate(self, calibrated_model: OnnxModel, **kwargs) -> OnnxModel:
        for cal_pass in self._pipelines:
            calibrated_model = cal_pass(calibrated_model, **kwargs)
        return calibrated_model

    def __add__(self, pipeline: "CalibrationPipeline") -> "CalibrationPipeline":
        _pipeline = CalibrationPipeline()
        _pipeline._pipelines = self._pipelines + pipeline._pipelines
        return _pipeline

    def __contains__(self, __x: CalibrationPass) -> bool:
        assert isinstance(__x, CalibrationPass), (
            "Calibration Pipeline only suppose to contain "
            + f"calibration passes, but got {__x!s}({type(__x)})."
        )
        return __x in self._pipelines

    def __iter__(self) -> Iterator[CalibrationPass]:
        return self._pipelines.__iter__()

    def __len__(self) -> int:
        return len(self._pipelines)

    def __str__(self) -> str:
        return "==>".join([str(cal_pass) for cal_pass in self._pipelines])
