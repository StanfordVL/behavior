import argparse
import inspect
import logging
import os

import igibson
from igibson.examples.learning.demo_replaying_batch import replay_demo_batch

import behavior
from behavior.examples.demo_segmentation_example import get_default_segmentation_processors


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_dir"] = os.path.join(igibson.ig_dataset_path, "tests")
    args_dict["demo_manifest"] = os.path.join(igibson.ig_dataset_path, "tests", "test_manifest.txt")
    args_dict["out_dir"] = os.path.join(behavior.examples_path, "data")
    if not defaults:
        parser = argparse.ArgumentParser(description="Segment a batch of BEHAVIOR demos in manifest.")
        parser.add_argument("demo_dir", type=str, help="Directory containing demos listed in the manifest.")
        parser.add_argument("demo_manifest", type=str, help="Plain text file consisting of list of demos to replay.")
        parser.add_argument("out_dir", type=str, help="Directory to store results in.")
        args = parser.parse_args()
        args_dict["demo_dir"] = args.demo_dir
        args_dict["demo_manifest"] = args.demo_manifest
        args_dict["out_dir"] = args.out_dir

    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Segment a batch of demos
    Use a manifest file to indicate the demos to segment
    """

    print("*" * 80 + "\nDescription:" + main.__doc__ + "\n" + "*" * 80)

    testing = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=testing)

    def get_segmentation_callbacks(**kwargs):
        # Create default segmentation processors.
        segmentation_processors = get_default_segmentation_processors()

        # Create a data callback that unifies the results from the
        # segmentation processors.
        def data_callback():
            data_cb_ret = dict()
            for name, sp in segmentation_processors.items():
                print("Serializing segmentation {}".format(name))
                data_cb_ret[name] = sp.serialize_segments()
            return data_cb_ret

        # Return all of the callbacks for a particular demo.
        return (
            [sp.start_callback for sp in segmentation_processors.values()],
            [sp.step_callback for sp in segmentation_processors.values()],
            [],
            [data_callback],
        )

    print("Run segmentation")
    replay_demo_batch(
        args_dict["demo_dir"],
        args_dict["demo_manifest"],
        args_dict["out_dir"],
        get_segmentation_callbacks,
        skip_existing=not testing,  # Do not skip when testing
        ignore_errors=not testing,  # Do not ignore when testing
    )
    print("Batch of demos segmented!")


RUN_AS_TEST = True  # Change to True to run this example in test mode
if __name__ == "__main__":
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
