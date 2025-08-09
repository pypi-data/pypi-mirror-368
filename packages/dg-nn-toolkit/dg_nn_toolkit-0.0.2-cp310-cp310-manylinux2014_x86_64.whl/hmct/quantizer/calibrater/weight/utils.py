from typing import List

from horizon_nn.ir import OnnxNode


def check_and_obtain_group_attribute(onnx_node: OnnxNode) -> int:
    groups: List[int] = []
    for next_op in onnx_node.next_ops:
        groups.append(next_op.attributes.get("group", 1))
    assert (
        len(set(groups)) == 1
    ), "It's invalid that different next_op has different group attribute value."

    return groups[0]
