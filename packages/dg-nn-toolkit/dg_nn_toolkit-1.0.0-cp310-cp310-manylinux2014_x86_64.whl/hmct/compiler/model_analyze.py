import argparse
from collections import Counter
import json
import os

from horizon_nn.ir.onnx_utils import load_model
from horizon_nn.utility import TEMP_DIR

from .compiler import build
from .hbdk_cc import hbdk_perf

# for character align in log
bpu_attribute_align_len = 0


def quantized_model_analyze(quantized_model):
    model = load_model(quantized_model)
    nodes = model.graph.node
    builder = build.HybridBuilder()
    builder.load_model(quantized_model)
    subgraph_num = builder.number_subgraphs
    node_graph_pair = {}
    for subgraph_id in range(subgraph_num):
        node_id_in_subgraph = builder.subgraph_node(subgraph_id)
        node_name_in_subgraph = [nodes[node_id].name for node_id in node_id_in_subgraph]
        node_subgraph_pair = dict(
            zip(node_name_in_subgraph, [subgraph_id] * len(node_id_in_subgraph)),
        )
        node_graph_pair.update(node_subgraph_pair)
    node_type_pair = {}
    for node_id in range(len(nodes)):
        node_name = nodes[node_id].name
        if node_name in node_graph_pair and nodes[node_id].op_type != "HzQuantize":
            node_type_pair[node_name] = node_graph_pair[node_name]
        else:
            node_type_pair[node_name] = -1
    return node_type_pair


def parse_json_generated_by_perf(json_content):
    summary = json_content["summary"]
    perf_keys = list(summary.keys())[:12]
    global bpu_attribute_align_len
    if not bpu_attribute_align_len:
        bpu_attribute_align_len = len(max(perf_keys, key=len))
    perf_pairs = [
        ": ".join([key.ljust(bpu_attribute_align_len, " "), str(summary[key])])
        for key in perf_keys
    ]
    return perf_pairs  # noqa: RET504


def hybrid_model_analyze(hybrid_model):
    model = load_model(hybrid_model)
    # get node name for each bpu node
    bpu_node_name = [
        node.name for node in model.graph.node if node.op_type == "HzBpuHBM"
    ]
    # get packed hbm model
    packed_hbm_model = model.graph.initializer[-1].string_data[0]
    # write packed hbm model to file
    packed_hbm_file = TEMP_DIR.relpath("packed_hbm_model.hbm")
    with open(packed_hbm_file, "wb") as f:
        f.write(packed_hbm_model)
    perf_output_dir = TEMP_DIR.mkdtemp()
    # do hbdk-perf
    hbdk_perf(packed_hbm_file, perf_output_dir)
    perf_result = {}
    for bpu_node in bpu_node_name:
        json_file = os.path.join(perf_output_dir, bpu_node + ".json")
        # parse hbdk-perf output
        with open(json_file) as f:
            json_content = json.load(f)
        perf_result[bpu_node] = parse_json_generated_by_perf(json_content)
    return perf_result


def format_quantized_analyze_result(quantized_analyze_result):
    max_node_name_len = len(max(quantized_analyze_result.keys(), key=len))
    aligned_line_len = max_node_name_len + 5
    pre_node_type = "CPU"
    subgraph_num = len(quantized_analyze_result)
    # count node num in each subgraph when iterating each node
    subgraph_node_cnt = dict(zip(range(-1, subgraph_num), [0] * (subgraph_num + 1)))
    # node num in each subgraph
    subgraph_node_num = Counter(quantized_analyze_result.values())
    format_result = []
    for node_name, subgraph_id in quantized_analyze_result.items():
        node_type = "BPU" if subgraph_id >= 0 else "CPU"
        subgraph_node_cnt[subgraph_id] += 1
        if node_type == "BPU" and pre_node_type == "CPU":
            pre_subgraph_id = subgraph_id
            # insert a line to state a bpu subgraph
            if subgraph_node_cnt[subgraph_id] == 1:
                head_line = "%s\n" % (
                    "STEP INTO SUBGRAPH %d".center(aligned_line_len, "-") % subgraph_id
                )
            else:
                head_line = "%s\n" % (
                    "IN SUBGRAPH %d".center(aligned_line_len, "-") % subgraph_id
                )
            format_result.append(head_line)
        elif node_type == "CPU" and pre_node_type == "BPU":
            # each node in the subgraph has been iterated
            if subgraph_node_cnt[pre_subgraph_id] == subgraph_node_num[pre_subgraph_id]:
                # insert a line to state a bpu subgraph end
                tail_line = "%s\n" % (
                    "OUT OF SUBGRAPH %d".center(aligned_line_len, "-") % pre_subgraph_id
                )
            else:
                # insert a line to state a bpu subgraph continue
                tail_line = "{}\n".format(
                    "TO BE CONTINUE".center(aligned_line_len, "-")
                )
            format_result.append(tail_line)
        # write current node type
        format_result.append(
            "{}: {}\n".format(node_name.ljust(max_node_name_len, " "), node_type),
        )
        pre_node_type = node_type

    return format_result


def format_hybrid_analyze_result(hybrid_analyze_result):
    format_result = []
    for subgraph_id, (_, bpu_node_info) in enumerate(hybrid_analyze_result.items()):
        format_result.append(
            "{}: {}\n".format(
                "SUBGRAPH ID".ljust(bpu_attribute_align_len, " "), subgraph_id
            ),
        )
        for info_item in bpu_node_info:
            format_result.append("" + info_item + "\n")
        format_result.append("\n")

    return format_result


def write_analyze_result_to_file(node_type_pair, bpu_node_detail):
    with open("model_analyze.txt", "w") as f:
        # write quantized model analyze result
        for line in format_quantized_analyze_result(node_type_pair):
            f.write(line)
        # insert a line
        f.write("\n")
        # write hybrid model analyze result
        for line in format_hybrid_analyze_result(bpu_node_detail):
            f.write(line)


def do_model_analyze(quantized_model, hybrid_model):
    # classify each node to CPU or BPU
    node_type_pair = quantized_model_analyze(quantized_model)
    # get bpu node details
    bpu_node_detail = hybrid_model_analyze(hybrid_model)
    # write analyze result to file
    write_analyze_result_to_file(node_type_pair, bpu_node_detail)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quantized_model",
        type=str,
        help="Input quantized model in onnx format.",
        required=True,
    )
    parser.add_argument(
        "--hybrid_model",
        type=str,
        help="Input hybrid model in onnx format.",
        required=True,
    )

    return parser.parse_args()


def main():
    args = get_args()
    do_model_analyze(args.quantized_model, args.hybrid_model)


if __name__ == "__main__":
    main()
