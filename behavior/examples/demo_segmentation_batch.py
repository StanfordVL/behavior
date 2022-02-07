import argparse
import inspect
import logging
import os
import sys

import behavior
from behavior.examples.demo_replay_batch import replay_demo_batch
from behavior.examples.demo_segmentation_example import get_default_segmentation_processors


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_root"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["log_manifest"] = os.path.join(
        os.path.dirname(inspect.getfile(behavior.examples)),
        "data",
        "test_manifest.txt",
    )
    args_dict["out_dir"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    if not defaults:
        parser = argparse.ArgumentParser(description="Segment a batch of BEHAVIOR demos in manifest.")
        parser.add_argument("demo_root", type=str, help="Directory containing demos listed in the manifest.")
        parser.add_argument("log_manifest", type=str, help="Plain text file consisting of list of demos to replay.")
        parser.add_argument("out_dir", type=str, help="Directory to store results in.")
        args = parser.parse_args()
        args_dict["demo_root"] = args.demo_root
        args_dict["log_manifest"] = args.log_manifest
        args_dict["out_dir"] = args.out_dir

    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Segment a batch of demos
    Use a manifest file to indicate the demos to segment
    """
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    def get_segmentation_callbacks(**kwargs):
        # Create default segmentation processors.
        segmentation_processors = get_default_segmentation_processors()

        # Create a data callback that unifies the results from the
        # segmentation processors.
        def data_callback():
            return {"segmentations": {name: sp.serialize_segments() for name, sp in segmentation_processors.items()}}

        # Return all of the callbacks for a particular demo.
        return (
            [sp.start_callback for sp in segmentation_processors.values()],
            [sp.step_callback for sp in segmentation_processors.values()],
            [],
            [data_callback],
        )

    replay_demo_batch(
        args_dict["demo_root"],
        args_dict["log_manifest"],
        args_dict["out_dir"],
        get_segmentation_callbacks,
        skip_existing=True,  # Do not skip when testing
    )


RUN_AS_TEST = False  # Change to True to run this example in test mode
if __name__ == "__main__":
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
