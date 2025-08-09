import argparse
import logging
import sys

from horizon_nn.common import HbdkDictParser
from horizon_nn.ir import OnnxModel
from horizon_nn.ir.onnx_utils import save_model

from .hybrid_build import HybridBuilder


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        help="Input onnx model(.onnx) file.",
        required=True,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output onnx model(.onnx) file name.",
        required=True,
    )
    parser.add_argument(
        "--march",
        type=str,
        choices=["bernoulli", "bernoulli2", "bayes", "bayes-e"],
        help="Target BPU micro architecture. Supported march: "
        "bernoulli; bernoulli2; bayes; bayes-e.",
    )
    parser.add_argument(
        "--hbdk_param",
        "-hbdk",
        type=str,
        help="Specify hbdk compilation parameters.",
    )

    return parser.parse_args(args)


def main(args):
    parser = parse_args(args)
    if parser.hbdk_param:
        hbdk_param = {"hbdk_pass_through_params": parser.hbdk_param}
    else:
        hbdk_param = {"hbdk_pass_through_params": "--O0"}
    hbdk_dict_parser = HbdkDictParser(hbdk_param)

    hybrid_build = HybridBuilder(
        OnnxModel(parser.model),
        parser.march,
        hbdk_dict_parser=hbdk_dict_parser,
        output_path="./",
    )
    hybrid_model = hybrid_build.hybrid_model()
    save_model(hybrid_model, parser.output)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
