import argparse

from horizon_nn.ir import OnnxModel
from horizon_nn.ir.onnx_utils import save_model

from .hybrid_build import HybridBuilder


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        help="Input onnx model(.onnx) file.",
        required=True,
    )
    parser.add_argument("--name", type=str, help="Submodel name prefix.", required=True)

    return parser.parse_args()


def main():
    args = get_args()
    hybrid_build = HybridBuilder(OnnxModel(args.model), None)
    hybrid_build.model_info()
    for g in range(hybrid_build.num_submodel()):
        submodel = hybrid_build.get_submodel(g)
        submodel_name = args.name + "_subgraph_" + str(g) + ".onnx"
        save_model(submodel, submodel_name)


if __name__ == "__main__":
    main()
