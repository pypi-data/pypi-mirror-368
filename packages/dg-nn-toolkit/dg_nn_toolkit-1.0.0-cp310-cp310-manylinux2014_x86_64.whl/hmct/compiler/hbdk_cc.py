import argparse
import logging
import shutil
import subprocess

__all__ = ["hbdk_cc", "hbdk_pack", "hbdk_perf", "hbdk_sim", "hbdk_model_check"]


def hbdk_sim(hbm_file, model_name, input_file, output_dir):
    """Simulate computation for hbm model.

    Args:
        hbm_file: hbm file name
        model_name: hbm model name to be simulated
        input_file: input data feeding to the hbm model
        output_dir: output dir to save simulation result
    """
    cmdlst = [
        "hbdk-sim",
        "-f",
        hbm_file,
        "-n",
        model_name,
        "-i",
        input_file,
        "-o",
        output_dir,
    ]
    proc = subprocess.Popen(cmdlst, stderr=subprocess.PIPE, universal_newlines=True)
    (out, err) = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"*** ERROR-OCCUR-DURING {{hbdk.hbdk-sim}} ***, error message: {err!s}"
        )


def hbdk_perf(hbm_file, output_dir):
    """Analyze performance for hbm model.

    Args:
        hbm_file: hbm file to be analyzed.
        output_dir: perf output dir (one json and html for each hbm model).
    """
    cmdlst = ["hbdk-perf", hbm_file, "-o", output_dir]
    proc = subprocess.Popen(cmdlst, stderr=subprocess.PIPE, universal_newlines=True)
    (out, err) = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"*** ERROR-OCCUR-DURING {{hbdk.hbdk-perf}} ***, "
            f"error message: {err!s}",
        )


def hbdk_pack(input_flist, output_file):
    """Pack multiple hbm file into one.

    Args:
        input_flist: hbm files to be packed.
        output_file: output file containing the packed model.

    Raises:
        RuntimeError: If compile failed.
    """
    cmdlst = ["hbdk-pack", *input_flist, "-o", output_file]
    proc = subprocess.Popen(cmdlst, stderr=subprocess.PIPE, universal_newlines=True)
    (out, err) = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"*** ERROR-OCCUR-DURING {{hbdk.hbdk-pack}} ***, "
            f"error message: {err!s}",
        )


def hbdk_model_check(hbir_model, march):
    """Check whether the hbir model is supported or not.

    Args:
      hbir_model: Input hbir model file.
      march: Target BPU micro architecture.

    Raises:
      RuntimeError: If check failed.
    """
    cmdlst = ["hbdk-model-check", "-f", "hbir", "-m", hbir_model, "--march", march]

    proc = subprocess.Popen(cmdlst, stderr=subprocess.PIPE, universal_newlines=True)
    (out, err) = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"*** ERROR-OCCUR-DURING {{hbdk.hbdk-model-check}} ***, "
            f"error message: {err!s}",
        )


def hbdk_cc(hbir_model, hbm_model, march, params=None, dump_all_models=False):
    """Compile the hbir model into a hbm model.

    Args:
      hbir_model: Input onnx or hbir model file.
      hbm_model: Output hbm model file.
      march: Target BPU micro architecture.
      params: Optional parameters for hbdk-cc.
      dump_all_models: Whether to save hbir model.

    Raises:
      RuntimeError: If compile failed.
    """
    # Do hbdk-model-check before hbdk-cc
    # hbdk_model_check(hbir_model, march)
    if params is None:
        params = []
    cmdlst = [
        "hbdk-cc",
        "-f",
        "hbir",
        "-m",
        hbir_model,
        "-o",
        hbm_model,
        "--march",
        march,
        "--progressbar",
    ]
    cmdlst += params
    hbdk_cmd = " ".join(cmdlst)
    logging.info(f"hbdk-cc parameters:{params}")
    logging.debug(f"hbdk-cc command used:{hbdk_cmd}")
    proc = subprocess.Popen(cmdlst, stderr=subprocess.PIPE, universal_newlines=True)
    (out, err) = proc.communicate()
    if proc.returncode != 0:
        # Save the hbir model that failed to compile.
        hbir_model_file = hbir_model.split("/")[-1]
        shutil.copyfile(hbir_model, hbir_model_file)
        logging.info(f"hbir_model saved: {hbir_model_file}")
        logging.info("-" * 70)
        logging.info(" ".join(cmdlst))
        logging.info(f"hbdk-cc failed to compile the {hbir_model} model.")
        logging.error(
            f"hbdk-cc compile hbir model failed with " f"returncode {proc.returncode}.",
        )
        raise RuntimeError(
            f"*** ERROR-OCCUR-DURING {{hbdk.hbdk-cc}} ***, " f"error message: {err!s}",
        )

    if dump_all_models:
        hbir_model_file = hbir_model.split("/")[-1]
        shutil.copyfile(hbir_model, hbir_model_file)
        logging.info(f"hbir_model has been saved as : {hbir_model_file}")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hbir",
        type=str,
        help="Input hbir model file name.",
        required=True,
    )
    parser.add_argument(
        "--hbm",
        type=str,
        help="Output hbm model file name.",
        required=True,
    )
    parser.add_argument(
        "--march",
        type=str,
        choices=["bernoulli", "bernoulli2"],
        help="Target BPU micro architecture. Supported march: "
        "bernoulli; bernoulli2.",
        required=True,
    )

    return parser.parse_args()


def main():
    args = get_args()
    hbdk_cc(args.hbir, args.hbm, args.march)


if __name__ == "__main__":
    main()
