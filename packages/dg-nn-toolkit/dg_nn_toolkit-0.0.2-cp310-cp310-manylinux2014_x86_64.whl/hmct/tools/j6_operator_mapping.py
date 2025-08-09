# This file is a original-float onnx to ptq onnx mapping dict which will be used
# by integration team


# node in this set will be converted to LUT.
lut_node_set = (
    "Abs",
    "Acos",
    "Acosh",
    "Asin",
    "Asinh",
    "Atan",
    "Ceil",
    "Atanh",
    "Cos",
    "Erf",
    "Floor",
    "Log",
    "Pow",
    "Reciprocal",
    "Round",
    "Sigmoid",
    "Sign",
    "Sin",
    "Sinh",
    "Sqrt",
    "Tan",
    "Tanh",
    "Celu",
    "Clip",
    "Elu",
    "Gelu",
    "HardSigmoid",
    "HardSwish",
    "LeakyRelu",
    "Mish",
    "PRelu",
    "Selu",
    "Softplus",
    "Softsign",
    "ThresholdedRelu",
)

# node in this set will be deleted/fused/folded, so the node will be fully supported.
fused_node_set = (
    "BatchNormalization",
    "Constant",
    "ConstantOfShape",
    "If",
    "Pad",
    "Shape",
    "Size",
    "Relu",
    "Dropout",
    "Identity",
)

# node in this map will be replaced to other node.
replaced_node_map = {
    "Flatten": "Reshape",
    "Gemm": "Conv",
    "Squeeze": "Reshape",
    "Sum": "Add",
    "Unsqueeze": "Reshape",
    "Upsample": "Reshape",
}

# node in this map will be splited to multiple nodes.
split_node_map = {
    "Div": [
        "HzLut",
        "Mul",
    ],
    "MatMul": [
        "MatMul",
        "Conv",
    ],
    "InstanceNormalization": [
        "ReduceMean",
        "Sub",
        "Mul",
        "Add",
        "HzLut",
    ],
    "LSTM": [
        "HzLut",
        "Split",
        "Mul",
        "Concat",
        "Transpose",
        "Add",
        "Conv",
    ],
    "GRU": [
        "Split",
        "Transpose",
        "MatMul",
        "Mul",
        "HzLut",
        "Add",
        "Reshape",
        "Sub",
        "Concat",
    ],
    "GroupNormalization": [
        "Reshape",
        "ReduceMean",
        "Sub",
        "Mul",
        "Add",
        "HzLut",
    ],
    "LayerNormalization": [
        "ReduceMean",
        "GlobalAveragePool",
        "Sub",
    ],
    "ReduceL1": [
        "HzLut",
        "ReduceSum",
    ],
    "ReduceL2": [
        "Pow",
        "ReduceSum",
        "Sqrt",
    ],
    "Softmax": [
        "Sub",
        "HzLut",
        "ReduceSum",
        "ReduceMax",
        "Reciprocal",
        "Mul",
    ],
}


def get_j6_hmct_node_mapping():
    """This func generate a list and is used by integration team.

        the structure of returned list like this:
        j6_hmct_node_mapping = [
            {
                "op_name": {
                    "op_list": []
                }
            }
        ]
    Note: Any change of the structure need to inform integration team.
    """
    j6_hmct_node_mapping = {}
    for node in lut_node_set:
        j6_hmct_node_mapping[node] = {"op_list": ["HzLut"]}
    for node in fused_node_set:
        j6_hmct_node_mapping[node] = {"op_list": ["None"]}
    for node, node_list in replaced_node_map.items():
        j6_hmct_node_mapping[node] = node_list
    for node, node_list in split_node_map.items():
        j6_hmct_node_mapping[node] = node_list
    return [j6_hmct_node_mapping]


if __name__ == "__main__":
    j6_hmct_node_mapping = get_j6_hmct_node_mapping()
    print(j6_hmct_node_mapping)
