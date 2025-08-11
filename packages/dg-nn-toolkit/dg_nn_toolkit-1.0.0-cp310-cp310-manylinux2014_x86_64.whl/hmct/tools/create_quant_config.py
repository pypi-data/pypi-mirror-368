import argparse
import os
import shutil


def create_quant_config(destination_path="./quant_config.json"):
    curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    source_path = os.path.join(curr_path, "../common/quant/quant_config.json")
    shutil.copy(source_path, destination_path)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        "-o",
        default="./quant_config.json",
        type=str,
        help="Output json file path.",
    )

    return parser.parse_args()


def main():
    args = get_args()
    create_quant_config(args.output)


if __name__ == "__main__":
    main()
