import argparse

from horizon_nn.ir.onnx_utils import ModelProto, load_model

from .compiler import build

__all__ = ["hbdk_onnx"]


def hbdk_onnx(model, hbir_file_name, march="bernoulli"):
    """Convert onnx model to hbir model.

    Args:
        model: ModelProto to convert.
        hbir_file_name: HBIR model file name to save.
        march: Architecture of BPU.

    Raises:
        ValueError: If input model is not of type ModelProto.
    """
    if not isinstance(model, ModelProto):
        raise ValueError(
            f"Optimizer only accepts ModelProto, incorrect type: {type(model)}",
        )

    model_str = model.SerializeToString()
    build.hbdk_onnx(model_str, hbir_file_name, march)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        help="Input fixed-point submodel in onnx format.",
        required=True,
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Name of the HBIR model.",
        required=True,
    )

    return parser.parse_args()


def main():
    args = get_args()
    onnx_model = load_model(args.model)
    hbdk_onnx(onnx_model, args.name)

    # show model convert model information
    s = ["-" * 60]
    output_name = [out.name for out in onnx_model.graph.output]
    s.append(f"ONNX model:       {args.model}")
    s.append(f"ONNX IR version:  {onnx_model.ir_version}")
    s.append(f"Opset version:    {onnx_model.opset_import[0].version}")
    s.append(f"Producer name:    {onnx_model.producer_name}")
    s.append(f"Producer version: {onnx_model.producer_version}")
    s.append(f"Model version:    {onnx_model.model_version}")
    s.append(f"Doc string:       {onnx_model.doc_string}")
    # s.append('Model Inputs:       '.format())
    s.append(f"Model Outputs:    {output_name}")
    s.append(f"HBIR model:       {args.name}")
    s += ["-" * 60]
    print("\n".join(s))


if __name__ == "__main__":
    main()
