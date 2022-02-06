import argparse
import glob
import logging
import os

import numpy as np
import pandas as pd


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_directory"] = "fixme"
    args_dict["split"] = "fixme"
    if not defaults:
        parser = argparse.ArgumentParser(description="Script to generate manifest for batch replay demos")
        parser.add_argument(
            "--demo_directory", type=str, required=True, help="Plain text file consisting of list of demos to replay"
        )
        parser.add_argument(
            "--split", type=int, default=0, help="Number of times to split the manifest for distributing replay"
        )
        args = parser.parse_args()
        args_dict["demo_directory"] = args.demo_directory
        args_dict["split"] = args.split
    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Generates a manifest file for batch processing of BEHAVIOR demos
    """
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    demos = glob.glob(os.path.join(args_dict["demo_directory"], "*.hdf5"))
    filtered_demos = [demo for demo in demos if "replay" not in demo]
    series = {"demos": filtered_demos}
    pd.DataFrame(series).to_csv("manifest.csv")
    if args_dict["split"] > 1:
        for idx, split in enumerate(np.array_split(filtered_demos, args_dict["split"])):
            pd.DataFrame({"demos": split}).to_csv("manifest_{}.csv".format(idx))


if __name__ == "__main__":
    main()
