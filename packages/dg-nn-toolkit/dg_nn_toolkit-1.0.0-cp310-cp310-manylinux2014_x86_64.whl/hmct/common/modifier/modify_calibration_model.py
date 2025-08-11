from collections import defaultdict
import logging
import re
from typing import Dict, List, Optional, Sequence, Union

import numpy as np
from tabulate import tabulate

from horizon_nn.ir import OnnxModel, load_model, save_model

from ..misc.find_calibration_node import find_input_calibration, find_output_calibration
from ..misc.node_relations import (
    node_inputs_calibration_relations,
    node_outputs_calibration_relations,
)
from ..misc.print_info_dict import print_info_dict

# yapf: disable
# Tensor Acceleration Engine Operators
TAE_OPS = ['Conv', 'ConvTranspose', 'MatMul']

# Vector Acceleration Engine Operators
VAE_OPS = [
    # elementwise ops
    'Add', 'Sub', 'Mul',
    # comparison ops
    'Equal', 'Greater', 'Less',
    # reduce ops
    'ReduceMax', 'ReduceMean', 'ReduceSum',
    # min/max ops
    'Min', 'Max', 'ArgMax', 'ArgMin',
    # activation ops
    'Sigmoid', 'HardSigmoid', 'Tanh', 'HzSwish', 'Softplus', 'HzMish', 'Celu',
    'HzHardSwish', 'HzGelu', 'LeakyRelu', 'Exp', 'Cos', 'Sin', 'Log', 'Clip',
    'Elu', 'Pow', 'HzRsqrt', 'Reciprocal', 'Sqrt', 'Abs', 'Atan', 'Floor',
    'Ceil', 'Acos', 'Acosh', 'Asin', 'Asinh', 'Atanh', 'Cosh', 'Erf', 'Selu',
    'Sinh', 'Tan',  'Round', 'Sign', 'Softsign', 'Relu', 'PRelu',
    # resize ops
    'Resize', 'HzResize11',
    # pooling ops
    'MaxPool', 'AveragePool', 'GlobalMaxPool', 'GlobalAveragePool',
    # other ops
    'GridSample', 'TopK', 'HzFilter', 'GridSamplePlugin',
]

# Data Transform Operators
TRANS_OPS = [
    'Reshape', 'Expand', 'Tile', 'Transpose', 'Concat', 'Pad', 'HzPad',
    'Slice', 'Split', 'HzChannelShuffle', 'Cast', 'Gather', 'GatherElements',
    # depthtospace and spacetodepth ops
    'HzDepthToSpace', 'DepthToSpace', 'HzSpaceToDepth', 'SpaceToDepth',
]
# yapf: enable

SUPPORT_QTYPES = [
    "float32",
    "float16",
    "bfloat16",
    "float8e4m3fn",
    "float8e5m2",
    "float8e3m4fn",
    "float8e2m5fn",
    "mxint8",
    "int32",
    "int16",
    "uint8",
    "int8",
    "int4",
]


def nodekind_to_b30engine(nodekind: str) -> Union[str, None]:
    if nodekind in TAE_OPS:
        return "TAE"
    if nodekind in VAE_OPS:
        return "VAE"
    if nodekind in TRANS_OPS:
        return "TRANS"
    return None


def index_input_threshold(node_attr, index: Union[str, int] = 0) -> Union[str, None]:
    return node_attr.get("InputThreshold" + str(index), None)


def index_input_type(node_attr, index: Union[str, int] = 0) -> Union[str, None]:
    if node_attr.get("InputType", None):
        return node_attr.get("InputType")
    return node_attr.get("InputType" + str(index), None)


def index_output_threshold(node_attr, index: Union[str, int] = 0) -> Union[str, None]:
    return node_attr.get("OutputThreshold" + str(index), None)


def index_output_type(node_attr, index: Union[str, int] = 0) -> Union[str, None]:
    if node_attr.get("OutputType", None):
        return node_attr.get("OutputType")
    return node_attr.get("OutputType" + str(index), None)


def sort_optimization(optimization: List[str]) -> List[str]:
    def rank_opt_config(opt_config: str) -> int:
        rank5_pattern = r"^set_all_nodes_.*$"
        rank10_pattern = r"^(set_.*_input_.*$|set_.*output_.*$)"
        if re.match(rank5_pattern, opt_config):
            return 5
        if re.match(rank10_pattern, opt_config):
            return 10
        return 0

    return sorted(optimization, key=lambda x: rank_opt_config(x))


def format_info(info: Union[Sequence[float], float, str, None]) -> Union[str, None]:
    if isinstance(info, Sequence):
        if len(info) > 1:
            return f"[{info[0]:.6f}, ...]"
        return f"{info[0]:.6f}"
    if isinstance(info, float):
        return f"{info:.6f}"
    return info


class CalibrationModifier:
    def __init__(self, model_or_file: Union[OnnxModel, str]):
        self.calibration_model = (
            model_or_file
            if isinstance(model_or_file, OnnxModel)
            else load_model(model_or_file)
        )

    def update_threshold(
        self,
        node_names: Union[str, List[str]],
        input_threshold: Union[List[float], np.ndarray, bytes] = None,
        output_threshold: Union[List[float], np.ndarray, bytes] = None,
    ) -> None:
        """调整节点阈值信息.

        对于校准节点, 可通过设置输入或者输出阈值修改, 同时设置输入和输出阈值时
        采用输出阈值;
        对于普通节点, 仅支持修改输入/输出在index0上的阈值.
        """
        if input_threshold is None and output_threshold is None:
            return
        if node_names is None:
            node_names = []
        if isinstance(node_names, str):
            node_names = [node_names]
        if input_threshold is not None:
            if isinstance(input_threshold, bytes):
                input_threshold = np.frombuffer(input_threshold, dtype=np.float32)
            input_threshold = np.array(input_threshold).astype(np.float32)
        if output_threshold is not None:
            if isinstance(output_threshold, bytes):
                output_threshold = np.frombuffer(output_threshold, dtype=np.float32)
            output_threshold = np.array(output_threshold).astype(np.float32)
        # 调整节点的输入/输出阈值信息
        for node in self.calibration_model.graph.nodes:
            if node.name not in node_names:
                continue
            if node.op_type == "HzCalibration":
                if input_threshold is not None:
                    node.thresholds = input_threshold
                if output_threshold is not None:
                    node.thresholds = output_threshold
            else:
                if input_threshold is not None:
                    calibration = find_input_calibration(node, 0)
                    if calibration is None:
                        continue
                    calibration.thresholds = input_threshold
                if output_threshold is not None:
                    calibration = find_output_calibration(node, 0)
                    if calibration is None:
                        continue
                    calibration.thresholds = output_threshold

    def update_qtype(
        self,
        node_names: Optional[Union[str, List[str]]] = None,
        node_kinds: Optional[Union[str, List[str]]] = None,
        input_qtype: Optional[str] = None,
        output_qtype: Optional[str] = None,
    ) -> None:
        """调整节点量化精度.

        对于校准节点, 可通过设置输入或者输出数据类型修改, 同时设置输入和输出数据类型时
        采用输出数据类型;
        对于普通节点, 指定input_qtype会修改所有输入的数据类型.
        """
        if input_qtype is None and output_qtype is None:
            return
        if node_names is None:
            node_names = []
        if isinstance(node_names, str):
            node_names = [node_names]
        if node_kinds is None:
            node_kinds = []
        if isinstance(node_kinds, str):
            node_kinds = [node_kinds]
        assert (
            input_qtype in SUPPORT_QTYPES or input_qtype is None
        ), f"input_qtype must in {SUPPORT_QTYPES}, but got {input_qtype}"
        assert (
            output_qtype in SUPPORT_QTYPES or output_qtype is None
        ), f"output_qtype must in {SUPPORT_QTYPES}, but got {output_qtype}"
        # 调整节点的输入/输出数据类型
        for node in self.calibration_model.graph.nodes:
            if node.name not in node_names and node.op_type not in node_kinds:
                continue
            if node.op_type == "HzCalibration":
                if input_qtype is not None:
                    node.qtype = input_qtype
                if output_qtype is not None:
                    node.qtype = output_qtype
            else:
                if input_qtype is not None:
                    for i in range(len(node.inputs)):
                        calibration = find_input_calibration(node, i)
                        if calibration is None:
                            continue
                        calibration.qtype = input_qtype
                if output_qtype is not None:
                    for i in range(len(node.outputs)):
                        calibration = find_output_calibration(node, i)
                        if calibration is None:
                            continue
                        calibration.qtype = output_qtype

    def update_with_dict(self, node_dict: Dict[str, Dict]) -> None:
        """按照node_dict的设置对模型进行更新."""
        for node in self.calibration_model.graph.nodes:
            if node.name not in node_dict:
                continue
            attr = node_dict[node.name]
            if node.op_type == "HzCalibration":
                self.update_threshold(
                    node_names=node.name,
                    input_threshold=index_input_threshold(attr),
                    output_threshold=index_output_type(attr),
                )
                self.update_qtype(
                    node_names=node.name,
                    input_qtype=index_input_type(attr),
                    output_qtype=index_output_type(attr),
                )
            else:
                for i in range(len(node.inputs)):
                    calibration = find_input_calibration(node, i)
                    if calibration is None:
                        continue
                    self.update_threshold(
                        node_names=calibration.name,
                        input_threshold=index_input_threshold(attr, i),
                    )
                    self.update_qtype(
                        node_names=calibration.name,
                        input_qtype=index_input_type(attr, i),
                    )
                for i in range(len(node.outputs)):
                    calibration = find_output_calibration(node, i)
                    if calibration is None:
                        continue
                    self.update_threshold(
                        node_names=calibration.name,
                        output_threshold=index_output_threshold(attr, i),
                    )
                    self.update_qtype(
                        node_names=calibration.name,
                        output_qtype=index_output_type(attr, i),
                    )

    def update_with_optimization(self, optimization: List[str]) -> None:
        """按照optimization的设置对模型进行更新."""
        for opt in sort_optimization(optimization):
            if opt.startswith("set_all_nodes_"):
                split_str_vec = opt.split("_")
                calibration_nodes = self.calibration_model.graph.type2nodes[
                    "HzCalibration"
                ]
                self.update_qtype(
                    node_names=[c.name for c in calibration_nodes],
                    input_qtype=split_str_vec[-1],
                )
            elif "_input_" in opt:
                split_str_vec = opt.split("_")
                self.update_qtype(
                    node_kinds=split_str_vec[1],
                    input_qtype=split_str_vec[-1],
                )
            elif "_output_" in opt:
                split_str_vec = opt.split("_")
                self.update_qtype(
                    node_kinds=split_str_vec[1],
                    output_qtype=split_str_vec[-1],
                )

    def visualize_calibrations(
        self,
        calibrations: Optional[Union[Sequence[str], str]] = None,
    ) -> None:
        """可视化校准节点量化参数信息."""
        if isinstance(calibrations, (str, Sequence)):
            calibrations = set(calibrations)
        elif calibrations is None:
            calibration_nodes = self.calibration_model.graph.type2nodes["HzCalibration"]
            calibrations = {c.name for c in calibration_nodes}
        else:
            raise TypeError(
                f"type(calibrations) should be str or "
                f"Sequence, but got {type(calibrations)}",
            )
        visualize_calibration_info = []
        headers = [
            "CalibrationNode",
            "Scales",
            "Thresholds",
            "ZeroPoint",
            "Qtype",
            "Granularity",
            "InputNodes",
            "OutputNodes",
        ]
        _, calibration_to_input_node = node_outputs_calibration_relations(
            self.calibration_model,
        )
        _, calibration_to_output_node = node_inputs_calibration_relations(
            self.calibration_model,
        )
        for node in self.calibration_model.graph.nodes:
            if node.name not in calibrations or node.op_type != "HzCalibration":
                continue
            visualize_calibration_info.append(
                [
                    node.name,
                    format_info(node.scales),
                    format_info(node.thresholds),
                    node.zero_point,
                    node.qtype,
                    node.granularity,
                    ",".join(calibration_to_input_node.get(node.name, [])),
                    ",".join(calibration_to_output_node.get(node.name, [])),
                ],
            )
        logging.info(
            f"Visualize Calibrations:\n"
            f"{tabulate(visualize_calibration_info, headers=headers)}"
        )

    def visualize_nodes(
        self, node_kinds: Optional[Union[Sequence[str], str]] = None
    ) -> None:
        """可视化普通节点输入输出信息."""
        if isinstance(node_kinds, (str, List)):
            node_kinds = set(node_kinds)
        elif node_kinds is None:
            node_kinds = {"Conv", "MatMul"}
        else:
            raise TypeError(
                "type(node_kinds) should be str or "
                f"Sequence, but got {type(node_kinds)}",
            )
        visualize_node_info = []
        calib_details = "Name,Scales,Thresholds,ZeroPoint,Qtype,Granularity"
        headers = [
            "Node",
            "OPType",
            f"InputCalibrations({calib_details})",
            f"WeightCalibrations({calib_details})",
            f"OutputCalibrations({calib_details})",
        ]
        for node_kind in node_kinds:
            for node in self.calibration_model.graph.type2nodes[node_kind]:
                # 获取输入激活和权重校准节点
                feature_calibrations, weight_calibrations = set(), set()
                for i in range(len(node.inputs)):
                    calibration_node = find_input_calibration(node, i)
                    if calibration_node is None:
                        continue
                    if calibration_node.tensor_type == "feature":
                        feature_calibrations.add(calibration_node)
                    if calibration_node.tensor_type == "weight":
                        weight_calibrations.add(calibration_node)
                # 获取输出校准节点
                output_calibrations = set()
                calibration_node = find_output_calibration(node)
                if calibration_node:
                    output_calibrations.add(calibration_node)
                visualize_node_info.append(
                    [
                        node.name,
                        node.op_type,
                        "\n".join(
                            [
                                f"{feature_calibration.name},{format_info(feature_calibration.scales)},{format_info(feature_calibration.thresholds)},{feature_calibration.zero_point},{feature_calibration.qtype},{feature_calibration.granularity}"
                                for feature_calibration in feature_calibrations
                            ],
                        ),
                        "\n".join(
                            [
                                f"{weight_calibration.name},{format_info(weight_calibration.scales)},{format_info(weight_calibration.thresholds)},{weight_calibration.zero_point},{weight_calibration.qtype},{weight_calibration.granularity}"
                                for weight_calibration in weight_calibrations
                            ],
                        ),
                        "\n".join(
                            [
                                f"{output_calibration.name},{format_info(output_calibration.scales)},{format_info(output_calibration.thresholds)},{output_calibration.zero_point},{output_calibration.qtype},{output_calibration.granularity}"
                                for output_calibration in output_calibrations
                            ],
                        ),
                    ],
                )
        logging.info(
            "Visualize Nodes({}):\n{}".format(
                ",".join(node_kinds),
                tabulate(visualize_node_info, headers=headers),
            ),
        )

    def visualize_qtypes(self, model_name="") -> None:
        """可视化TAE, VAE和TRANS算子的数据类型."""
        qtypes_info = defaultdict(dict)
        tae_num, vae_num, trans_num = 0, 0, 0
        for qtype in SUPPORT_QTYPES:
            for b30engine in ["TAE", "VAE", "TRANS"]:
                qtypes_info[qtype][b30engine] = 0
        # 遍历节点获取TAE,VAE,TRANS的数量以及数据类型情况
        for node in self.calibration_model.graph.nodes:
            if node.op_type == "HzCalibration":
                continue
            node_b30engine = nodekind_to_b30engine(node.op_type)
            if node_b30engine == "TAE":
                tae_num += 1
            elif node_b30engine == "VAE":
                vae_num += 1
            elif node_b30engine == "TRANS":
                trans_num += 1
            else:
                logging.warning(f"The engine of {node.name} is None.")
                continue
            # 获取节点的输入数据类型
            input_qtypes = set()
            for i in range(len(node.inputs)):
                calibration_node = find_input_calibration(node, i)
                if calibration_node is None:
                    continue
                input_qtypes.add(calibration_node.qtype)
            # 记录特定b30engine的数据类型
            find_unknown_qtype = True
            for qtype in SUPPORT_QTYPES:
                if qtype in input_qtypes:
                    qtypes_info[qtype][node_b30engine] += 1
                    find_unknown_qtype = False
                    break
            if find_unknown_qtype:
                qtypes_info["float32"][node_b30engine] += 1
        # 汇总基于b30engine的数据类型分析结果
        for b30engine in ["TAE", "VAE", "TRANS"]:
            qtypes_info["ALL"][b30engine] = (
                f"{sum([qtypes_info[_][b30engine] for _ in SUPPORT_QTYPES])}/"
                f"{tae_num + vae_num + trans_num}"
            )
        for qtype in SUPPORT_QTYPES:
            qtypes_info[qtype]["ALL"] = "{}/{}".format(
                sum([qtypes_info[qtype][_] for _ in ["TAE", "VAE", "TRANS"]]),
                tae_num + vae_num + trans_num,
            )
        qtypes_info["ALL"]["ALL"] = (
            f"{tae_num + vae_num + trans_num}/{tae_num + vae_num + trans_num}"
        )
        print_info_dict(
            qtypes_info,
            title="Visualize Qtypes " + model_name,
            key_type="Qtype",
        )

    def get_model(self, save_path=None) -> OnnxModel:
        if save_path:
            save_model(self.calibration_model, save_path)
        return self.calibration_model
