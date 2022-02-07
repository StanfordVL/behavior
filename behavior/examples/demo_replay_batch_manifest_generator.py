import argparse
import glob
import inspect
import logging
import os
import sys

import numpy as np
import pandas as pd

import behavior


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_directory"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["split"] = 0
    if not defaults:
        parser = argparse.ArgumentParser(description="Script to generate manifest for batch replay demos")
        # TODO: there is a mismatch between the description of demo_directory and the use in the code. in the code it is
        # expected to be a directory (like the name indicates) containing hdf5 files and we will add all the files
        # But the description says it should be a text file? there was also a text file in iG "test_manifest.txt"
        # Reverting to what the code expects
        # parser.add_argument(
        #     "--demo_directory", type=str, required=True, help="Plain text file consisting of list of demos to replay"
        # )
        parser.add_argument(
            "--demo_directory",
            type=str,
            required=True,
            help="Directory containing a group of demos to replay with a manifest",
        )
        parser.add_argument(
            "--split",
            type=int,
            default=args_dict["split"],
            help="Number of times to split the manifest for distributing replay",
        )
        args = parser.parse_args()
        args_dict["demo_directory"] = args.demo_directory
        args_dict["split"] = args.split
    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Generates a manifest file for batch processing of BEHAVIOR demos
    """
    logging.getLogger().setLevel(logging.INFO)
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    demos = glob.glob(os.path.join(args_dict["demo_directory"], "*.hdf5"))
    logging.info("Demos to add to the manifest: {}".format(demos))
    filtered_demos = [demo for demo in demos if "replay" not in demo]
    logging.info("Demos to add to the manifest after removing replays: {}".format(demos))
    series = {"demos": filtered_demos}
    output_folder = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    pd.DataFrame(series).to_csv(os.path.join(output_folder, "manifest.csv"))
    if args_dict["split"] > 1:
        for idx, split in enumerate(np.array_split(filtered_demos, args_dict["split"])):
            pd.DataFrame({"demos": split}).to_csv(os.path.join(output_folder, "manifest_{}.csv".format(idx)))

    logging.info("Manifest(s) created")


if __name__ == "__main__":
    if sys.argv[1] == "--test":
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
