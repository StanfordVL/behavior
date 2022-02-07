import argparse
import glob
import inspect
import logging
import os
import subprocess
import sys

import igibson
import tqdm

import behavior
import behavior.examples


def parse_args(defaults=False):

    args_dict = dict()
    args_dict["demo_directory"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["segmentation_directory"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["results_directory"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")

    if not defaults:
        parser = argparse.ArgumentParser(description="Script to batch-replay segmented demos using action primitives.")
        parser.add_argument("demo_directory", type=str, help="Path to directory containing demos")
        parser.add_argument("segmentation_directory", type=str, help="Path to directory containing demo segmentations")
        parser.add_argument("results_directory", type=str, help="Path to directory to store results in")
        args = parser.parse_args()
        args_dict["demo_directory"] = args.demo_directory
        args_dict["segmentation_directory"] = args.segmentation_directory
        args_dict["results_directory"] = args.results_directory

    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Replays a batch of demos using action primitives
    Creates threads for a batch of demos to be replayed in parallel
    Uses the code in replay_demo_with_action_primitives.py
    """
    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    skip_if_existing = not defaults  # Not skipping if testing

    logging.info(
        "Segmentations to run: {}".format(
            len(list(glob.glob(os.path.join(args_dict["segmentation_directory"], "*.json"))))
        )
    )

    # Load the demo to get info
    for demo_fullpath in tqdm.tqdm(list(glob.glob(os.path.join(args_dict["segmentation_directory"], "*.json")))):
        demo = os.path.splitext(os.path.basename(demo_fullpath))[0]
        if "replay" in demo:
            continue

        demo_path = os.path.join(args_dict["demo_directory"], demo + ".hdf5")
        segmentation_path = os.path.join(args_dict["segmentation_directory"], demo + "_segm.json")
        output_path = os.path.join(args_dict["results_directory"], demo + "_ap_replay.json")
        log_path = os.path.join(args_dict["results_directory"], demo + "_ap_replay.log")

        if os.path.exists(output_path) and skip_if_existing:
            logging.info("Skipping demo because it exists already: {}".format(output_path))
            continue

        # Batch me
        script_path = os.path.join(igibson.example_path, "behavior", "replay_demo_with_action_primitives.py")
        command = ["python", script_path, demo_path, segmentation_path, output_path]

        with open(log_path, "w") as log_file:
            logging.info("Launching subprocess for demo. Command: {}. Log file: {}".format(command, log_path))
            tqdm.tqdm.write("Processing %s" % demo)
            subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT)


RUN_AS_TEST = False  # Change to True to run this example in test mode
if __name__ == "__main__":
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
