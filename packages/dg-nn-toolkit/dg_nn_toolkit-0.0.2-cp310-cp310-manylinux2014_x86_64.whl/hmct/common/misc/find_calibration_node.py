from typing import Optional, Union

from horizon_nn.ir import CalibrationNode, OnnxNode


def can_be_skipped(node: OnnxNode) -> bool:
    """判断向前或者向后查找校准节点的时候, 遇到的节点是否可以跳过."""
    if node.op_type in [
        "MaxPool",
        "GlobalMaxPool",
        "Relu",
        "Reshape",
        "Transpose",
        "ReduceMax",
        "Split",
        "Slice",
        "Gather",
        "ScatterND",
    ]:
        return True

    return False


def find_input_calibration(
    node: OnnxNode,
    index: Union[None, int] = None,
) -> Optional[CalibrationNode]:
    """找到一个普通节点输入的校准节点.

    Args:
        node: 普通非校准节点, 用于对其输入寻找校准节点.
        index: 如果是None, 依次遍历节点各个输入, 返回找到的第一个校准节点;
               如果不是None, 返回指定输入对应的校准节点.

    Returns:
        如果找到返回相应校准节点, 否则返回None.
    """
    if len(node.prev_ops) > 0:
        if index is None and node.op_type in ["ScatterND"]:
            # ScatterND节点的输入0是data, 如果没有明确指定index, 默认查找data输入上的校准节点.
            index = 0
        if index is None:
            for prev in node.prev_ops:
                if prev.op_type == "HzCalibration":
                    return prev
            for prev in node.prev_ops:
                if can_be_skipped(prev):
                    return find_input_calibration(prev)
        elif node.inputs[index].src_op is not None:
            prev = node.inputs[index].src_op
            if prev.op_type == "HzCalibration":
                return prev
            if can_be_skipped(prev):
                return find_input_calibration(prev)

    return None


def find_output_calibration(
    node: OnnxNode,
    index: Union[None, int] = None,
) -> Optional[CalibrationNode]:
    """找到一个普通节点输出的校准节点.

    Args:
        node: 普通非校准节点, 用于对其输出寻找校准节点.
        index: 如果为None, 依次遍历节点各个输出, 返回找到的第一个校准节点;
            如果为非None,返回指定输出对应的校准节点.

    Returns:
        如果找到返回相应校准节点, 否则返回None.
    """
    # Conv+ResNetAdd结构需要找到ResNetAdd后面的校准节点.
    if (
        node.op_type == "Conv"
        and len(node.outputs[0].dest_ops) == 1
        and node.outputs[0].dest_op.op_type == "Add"
    ):
        return find_output_calibration(node.outputs[0].dest_op)

    candidate_nodes = (
        list(node.next_ops) if index is None else list(node.outputs[index].dest_ops)
    )
    while candidate_nodes:
        n = candidate_nodes.pop(0)
        if n.op_type == "HzCalibration":
            return n
        if can_be_skipped(n):
            candidate_nodes.extend(list(n.next_ops))

    return None
