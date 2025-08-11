import numpy as np

from horizon_nn.ir import OnnxModel, OnnxNode

from .pass_base import PredicateBasedPass


class ConstantToInitializer(PredicateBasedPass):
    @property
    def name(self) -> str:
        return "replace_constant_with_initializer"

    def match_pattern(self, onnx_node: OnnxNode) -> bool:
        if onnx_node.op_type == "Constant":
            return True

        return False

    def apply_transform(self, onnx_node: OnnxNode, onnx_model: OnnxModel) -> bool:
        if "value" in onnx_node.attributes:
            output_value = onnx_node.attributes["value"].value
        elif "value_float" in onnx_node.attributes:
            output_value = np.array(
                onnx_node.attributes["value_float"], dtype=np.float32
            )
        elif "value_floats" in onnx_node.attributes:
            output_value = np.array(
                onnx_node.attributes["value_floats"], dtype=np.float32
            )
        elif "value_int" in onnx_node.attributes:
            output_value = np.array(onnx_node.attributes["value_int"], dtype=np.int64)
        elif "value_ints" in onnx_node.attributes:
            output_value = np.array(onnx_node.attributes["value_ints"], dtype=np.int64)
        else:
            raise NotImplementedError(
                f"Unsupported Constant attribute: {onnx_node.attributes}"
            )

        # 对当前算子进行常量折叠
        output_var = onnx_model.graph.create_variable(
            name=onnx_node.outputs[0].name,
            is_param=True,
            value=output_value,
        )
        onnx_node.outputs[0].replace_all_uses_with(output_var)
        # destroy folded node
        onnx_node.destroy()

        return True
