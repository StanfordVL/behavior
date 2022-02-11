import argparse
import inspect
import logging
import os
import sys

import igibson
from igibson.examples.learning.demo_replaying_batch import replay_demo_batch
from igibson.metrics.agent import RobotMetric
from igibson.metrics.disarrangement import KinematicDisarrangement, LogicalDisarrangement
from igibson.metrics.gaze import GazeMetric
from igibson.metrics.task import TaskMetric

import behavior
import behavior.examples


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_dir"] = os.path.join(igibson.ig_dataset_path, "tests")
    args_dict["demo_manifest"] = os.path.join(igibson.ig_dataset_path, "tests", "test_manifest.txt")
    args_dict["out_dir"] = os.path.join(behavior.examples_path, "data")
    if not defaults:
        parser = argparse.ArgumentParser(description="Collect metrics from BEHAVIOR demos in manifest.")
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
    Compute metrics on a batch of previously recorded demos
    Uses a manifest file
    """

    print("*" * 80 + "\nDescription:" + main.__doc__ + "/n" + "*" * 80)

    testing = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=testing)

    def get_metrics_callbacks(**kwargs):
        metrics = [
            KinematicDisarrangement(),
            LogicalDisarrangement(),
            RobotMetric(),
            GazeMetric(),
            TaskMetric(),
        ]

        return (
            [metric.start_callback for metric in metrics],
            [metric.step_callback for metric in metrics],
            [metric.end_callback for metric in metrics],
            [metric.gather_results for metric in metrics],
        )

    replay_demo_batch(
        args_dict["demo_dir"],
        args_dict["demo_manifest"],
        args_dict["out_dir"],
        get_metrics_callbacks,
        skip_existing=not testing,  # Do not skip when testing
        ignore_errors=not testing,  # Do not ignore when testing
    )


RUN_AS_TEST = False  # Change to True to run this example in test mode
if __name__ == "__main__":
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
