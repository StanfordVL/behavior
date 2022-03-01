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
    args_dict["demo_dir"] = os.path.join(igibson.ig_dataset_path, "tests")
    args_dict["segm_dir"] = os.path.join(behavior.examples_path, "data")
    args_dict["out_dir"] = os.path.join(behavior.examples_path, "data")

    if not defaults:
        parser = argparse.ArgumentParser(description="Script to batch-replay segmented demos using action primitives.")
        parser.add_argument("demo_dir", type=str, help="Path to directory containing demos")
        parser.add_argument("segm_dir", type=str, help="Path to directory containing demo segmentations")
        parser.add_argument("out_dir", type=str, help="Path to directory to store results in")
        args = parser.parse_args()
        args_dict["demo_dir"] = args.demo_dir
        args_dict["segm_dir"] = args.segm_dir
        args_dict["out_dir"] = args.out_dir

    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Replays a batch of demos using action primitives
    Creates threads for a batch of demos to be replayed in parallel
    Uses the code in replay_demo_with_action_primitives.py
    """

    print("*" * 80 + "\nDescription:" + main.__doc__ + "\n" + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    skip_if_existing = not defaults  # Not skipping if testing

    # Find all the segmentation files by searching for json files in the segmentation directory
    segm_files = list(glob.glob(os.path.join(args_dict["segm_dir"], "*_segm.json")))
    demo_files = list(glob.glob(os.path.join(args_dict["demo_dir"], "*.hdf5")))

    print("Segmentations to replay with action primitives: {}".format(len(segm_files)))

    # Load the demo to get info
    for demo_file in tqdm.tqdm(demo_files):
        demo = os.path.splitext(os.path.basename(demo_file))[0]
        if "replay" in demo:
            continue

        for segm_file in segm_files:
            if demo in segm_file:
                segm_name = os.path.splitext(os.path.basename(segm_file))[0]
                ap_replay_demo_file = os.path.join(args_dict["out_dir"], segm_name + "_ap_replay.json")
                out_log_file = os.path.join(args_dict["out_dir"], segm_name + "_ap_replay.log")

                if os.path.exists(ap_replay_demo_file) and skip_if_existing:
                    print("Skipping demo because it exists already: {}".format(ap_replay_demo_file))
                    continue

                # Batch me
                script_file = os.path.join(behavior.examples_path, "replay_demo_with_action_primitives_example.py")
                command = ["python", script_file, demo_file, segm_file, ap_replay_demo_file]

                with open(out_log_file, "w") as log_file:
                    print("Launching subprocess for demo. Command: {}. Log file: {}".format(command, out_log_file))
                    tqdm.tqdm.write("Processing %s" % demo)
                    subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT)


RUN_AS_TEST = False  # Change to True to run this example in test mode
if __name__ == "__main__":
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
