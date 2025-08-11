import logging
from typing import Optional

from horizon_nn.common import HbdkDictParser
from horizon_nn.ir import OnnxModel, serialize_model
from horizon_nn.ir.onnx_utils import (
    TensorProto,
    checker,
    helper,
    load_model_from_string,
)
from horizon_nn.utility import TEMP_DIR

from .compiler import build
from .hbdk_cc import hbdk_cc, hbdk_pack, hbdk_perf
from .hbdk_onnx import hbdk_onnx
from .utils import make_string_tensor


class HybridBuilder:
    """This class is used to make hybrid model."""

    def __init__(
        self,
        onnx_model: OnnxModel,
        bpu_march: str,
        hbdk_dict_parser: HbdkDictParser,
        output_path: Optional[str] = None,
        dump_all_models: bool = False,
    ) -> None:
        self.onnx_model = onnx_model
        self.quantized_model = None
        self.bpu_march = bpu_march
        self.submodel_with_filter = {}
        self._load_model()
        self.build_hbm = bpu_march is not None
        self.hbdk_dict_parser = hbdk_dict_parser
        self.dump_all_models = dump_all_models
        self.output_path = output_path
        self._builder.set_pyramid_input_list(self.get_pyramid_input_list())

    def _load_model(self):
        self._builder = build.HybridBuilder()
        self._builder.set_march(self.bpu_march)

        self.quantized_model = self.onnx_model.proto
        self._builder.load_model(serialize_model(self.onnx_model))

        self.number_of_submodels = self._builder.number_subgraphs
        init_names = [init.name for init in self.quantized_model.graph.initializer]
        self.graph_input = [
            i for i in self.quantized_model.graph.input if i.name not in init_names
        ]
        if len(self.graph_input) == 0:
            raise ValueError("can't find input in quantize model.")

    def num_submodel(self):
        return self.number_of_submodels

    def get_subgraph_nodes(self, idx):
        return self._builder.subgraph_node(idx)

    def get_submodel(self, idx):
        assert idx < self.number_of_submodels
        submodel_str = self._builder.submodel(idx)
        return load_model_from_string(submodel_str)

    # if input comes from pyramid or resizer, it will be saved
    # in the list and return
    def get_pyramid_input_list(self):
        ret_list = []
        input_source_dict = self.hbdk_dict_parser.get_input_source()
        if not input_source_dict:
            return ret_list

        # parse input_source_dict
        input_info_dict = {}
        for item in self.graph_input:
            if input_source_dict.get(item.name):
                input_info_dict[item.name] = input_source_dict[item.name]
            else:
                input_info_dict[item.name] = input_source_dict["_default_value"]

        for item in input_info_dict:
            if input_info_dict[item] in ("pyramid", "resizer"):
                ret_list.append(item)
        return ret_list

    def get_input_split(self, model):
        graph_input = [
            n.output[0] for n in model.graph.node if n.op_type == "HzQuantize"
        ]
        input_split = []
        for i in graph_input:
            if i in self.input_split:
                input_split.append(self.input_split[i])
        return (
            {}
            if len(input_split) == 0
            else {"split-by-input-dims": ",".join(input_split)}
        )

    def get_subgraph_layout(self, sub_graph_name):
        sub_graph_layout = self._builder.subgraph_layout(sub_graph_name)
        input_layout, output_layout = sub_graph_layout
        return {"input-layout": input_layout, "output-layout": output_layout}

    def get_submodel_hbm(self, name):
        idx = int(name.split("_")[-1])
        assert idx < self.number_of_submodels
        logging.info(f"Compile submodel: {name}")
        submodel_str = self._builder.submodel(idx)
        submodel = load_model_from_string(submodel_str)
        for node in submodel.graph.node:
            if node.op_type == "HzQuantizedFilter":
                self.submodel_with_filter[name] = True
        hbir_model = TEMP_DIR.relpath(name + ".hbir")
        hbm_model = TEMP_DIR.relpath(name + ".hbm")
        hbdk_onnx(submodel, hbir_model, self.bpu_march)
        graph_input = [
            n.output[0] for n in submodel.graph.node if n.op_type == "HzQuantize"
        ]
        subgraph_layout = self.get_subgraph_layout(name)
        hbdk_params = self.hbdk_dict_parser.generate_options_for_cc(
            graph_input,
            **subgraph_layout,
        )
        hbdk_cc(
            hbir_model,
            hbm_model,
            self.bpu_march,
            hbdk_params,
            self.dump_all_models,
        )
        if self.output_path is not None:
            hbdk_perf(hbm_model, self.output_path)
        return hbm_model

    def hybrid_model(self):
        hybrid_model_str = self._builder.hybrid_model(self.build_hbm)
        hybrid_model = load_model_from_string(hybrid_model_str)
        if self.build_hbm:
            packed_hbm_name = "PACKED_HBM_MODEL"
            hbm_flist = []
            for node in hybrid_model.graph.node:
                if node.op_type == "HzBpuHBM":
                    # For HzBpuHBM node, its node name format is xxx_{id},
                    # where {id} indicates the index of the corresponding
                    # subgraph.
                    hbm_flist.append(self.get_submodel_hbm(node.name))
                    node.input.extend([packed_hbm_name])
                    if self.submodel_with_filter.get(node.name, False):
                        attr = helper.make_attribute("with_filter", 1)
                        node.attribute.extend([attr])
            packed_model = TEMP_DIR.relpath("packed_model.hbm")
            hbdk_pack(hbm_flist, packed_model)
            with open(packed_model, "rb") as f:
                packed_val = f.read()
            tensor = make_string_tensor(
                name=packed_hbm_name,
                data_type=TensorProto.STRING,
                dims=[],
                vals=[packed_val],
            )
            hybrid_model.graph.initializer.extend([tensor])
            tensor_info = helper.make_tensor_value_info(
                name=packed_hbm_name,
                elem_type=TensorProto.STRING,
                shape=[],
            )
            hybrid_model.graph.input.extend([tensor_info])
            checker.check_model(hybrid_model)

        return hybrid_model

    def model_info(self, log_file=None):
        graph_nodes = self.quantized_model.graph.node
        node_names = [node.name for node in graph_nodes]
        longest_node_name_length = len(max(node_names, key=len))
        node_subgraph_map = {}
        subgraph_node_map = {}
        for subgraph_id in range(self.number_of_submodels):
            # For easy conversion to HBDK model, the generated subgraph
            # contains the HzQuantize node.
            _subgraph_nodes = self.get_subgraph_nodes(subgraph_id)
            subgraph_nodes = []
            for node_id in _subgraph_nodes:
                if graph_nodes[node_id].op_type != "HzQuantize":
                    # HzQuantize node is actually executed on the CPU.
                    subgraph_nodes.append(node_id)
                    node_subgraph_map[graph_nodes[node_id].name] = subgraph_id
            subgraph_node_map[subgraph_id] = subgraph_nodes

        node_info = {}
        log_format = "{:<" + f"{longest_node_name_length}" + "} {:<5}"
        hdr = log_format.format("Node", "Type")
        split_line_len = longest_node_name_length + 5
        s = ["The node information of hybrid model:", "-" * split_line_len, hdr]

        pre_node_id = -1
        pre_subgraph_id = -1
        for node_id, node in enumerate(graph_nodes):
            if (
                node.op_type in ("HzDequantize", "HzQuantize", "HzDequantizeFilter")
                or node.op_type in ("Transpose", "Reshape")
                and (
                    "NCHW2NHWC_LayoutConvert" in node.name
                    or "NHWC2NCHW_LayoutConvert" in node.name
                )
            ):
                continue
            subgraph_id = node_subgraph_map.get(node.name, -1)
            node_type = "BPU" if subgraph_id >= 0 else "CPU"
            if subgraph_id != pre_subgraph_id:
                if pre_subgraph_id >= 0:
                    if pre_node_id == subgraph_node_map[pre_subgraph_id][-1]:
                        s.append(
                            "End Subgraph {}".center(split_line_len, "-").format(
                                pre_subgraph_id,
                            ),
                        )
                    else:
                        s.append("-" * split_line_len)

                if subgraph_id >= 0:
                    if node_id == subgraph_node_map[subgraph_id][0]:
                        s.append(
                            "Start Subgraph {}".center(split_line_len, "-").format(
                                subgraph_id,
                            ),
                        )
                    else:
                        s.append(
                            "Subgraph {}".center(split_line_len, "-").format(
                                subgraph_id,
                            ),
                        )
            subgraph_str = "--"
            if node.name in node_subgraph_map:
                subgraph_str = f"id({node_subgraph_map[node.name]!s})"
            s.append(log_format.format(node.name, node_type))
            node_info.update(
                {
                    node.name: {
                        "ON": node_type,
                        "Subgraph": subgraph_str,
                        "Type": node.op_type,
                    },
                },
            )
            pre_node_id = node_id
            pre_subgraph_id = subgraph_id
        s.append("End".center(split_line_len, "-"))
        if log_file is not None:
            with open(log_file, "w") as f:
                f.write("\n".join(s))
        return node_info
