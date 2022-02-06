"""
  Script to convert BEHAVIOR virtual reality demos to dataset compatible with imitation learning
"""

import argparse
import inspect
import json
import logging
import os
from pathlib import Path

import h5py
import igibson
import numpy as np
import pandas as pd
from igibson.metrics.dataset import DatasetMetric
from igibson.utils.ig_logging import IGLogReader
from igibson.utils.utils import parse_config

import behavior
from behavior.examples.demo_replay_example import replay_demo


def save_episode(in_log_path, dataset_metric):
    episode_identifier = "_".join(os.path.splitext(in_log_path)[0].split("_")[-2:])
    episode_out_log_path = "processed_hdf5s/{}_{}_{}_{}_{}_episode.hdf5".format(
        activity, activity_id, scene, instance_id, episode_identifier
    )
    hf = h5py.File(episode_out_log_path, "w")

    # Copy the metadata
    for attr in IGLogReader.get_all_metadata_attrs(in_log_path):
        hf.attrs[attr] = IGLogReader.read_metadata_attr(in_log_path, attr)

    for key, value in dataset_metric.gather_results().items():
        if key == "action":
            dtype = np.float64
        else:
            dtype = np.float32
        hf.create_dataset(key, data=np.stack(value), dtype=dtype, compression="lzf")

    hf.close()


def generate_il_dataset(
    demo_root,
    log_manifest,
    out_dir,
    config_file=os.path.join(igibson.example_config_path, "behavior_full_observability.yaml"),
    skip_existing=True,
    save_frames=False,
    deactivate_logger=True,
):
    """
    Extract pairs of (observation,action) for imitation learning from a batch of BEHAVIOR demos.

    @param demo_root: Directory containing the demo files listed in the manifests.
    @param log_manifest: The manifest file containing list of BEHAVIOR demos to batch over.
    @param out_dir: Directory to store results in.
    @param config_file: environment config file
    @param skip_existing: Whether demos with existing output logs should be skipped.
    @param save_frames: Whether the demo's frames should be saved alongside statistics.
    @param deactivate_logger: If we deactivate the logger
    """

    if deactivate_logger:
        logger = logging.getLogger()
        logger.disabled = True

    demo_list = pd.read_csv(log_manifest)

    config = parse_config(config_file)
    # should NOT activate behavior robot to be consistent with VR demo collection setup
    config["should_activate_behavior_robot"] = False
    # highlight task relevant objects because the observation includes "highlight"
    config["should_highlight_task_relevant_objs"] = True

    for idx, demo in enumerate(demo_list["demos"]):
        if "replay" in demo:
            continue

        demo_name = os.path.splitext(demo)[0]
        demo_path = os.path.join(demo_root, demo)
        log_path = os.path.join(out_dir, demo_name + ".json")

        if skip_existing and os.path.exists(log_path):
            logging.info("Skipping existing demo: {}, {} out of {}".format(demo, idx, len(demo_list["demos"])))
            continue

        logging.info("Replaying demo: {}, {} out of {}".format(demo, idx, len(demo_list["demos"])))

        curr_frame_save_path = None
        if save_frames:
            curr_frame_save_path = os.path.join(out_dir, demo_name + ".mp4")

        try:
            dataset = DatasetMetric()
            demo_information = replay_demo(
                in_log_path=demo_path,
                frame_save_path=curr_frame_save_path,
                mode="headless",
                config_file=config_file,
                verbose=False,
                image_size=(128, 128),
                start_callbacks=[dataset.start_callback],
                step_callbacks=[dataset.step_callback],
                end_callbacks=[dataset.end_callback],
            )
            demo_information["failed"] = False
            demo_information["filename"] = Path(demo).name
            save_episode(demo_path, dataset)

        except Exception as e:
            logging.error("Demo failed withe error: {}".format(e))
            demo_information = {"demo_id": Path(demo).name, "failed": True, "failure_reason": str(e)}

        logging.info("Saving data")
        with open(log_path, "w") as file:
            json.dump(demo_information, file)


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_root"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["log_manifest"] = os.path.join(
        os.path.dirname(inspect.getfile(behavior.examples)), "data", "test_manifest.txt"
    )
    args_dict["out_dir"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["config"] = os.path.join(os.path.dirname(inspect.getfile(behavior)), "configs", "behavior_vr.yaml")
    if not defaults:
        parser = argparse.ArgumentParser(
            description="Extract pairs of (observation,action) for imitation learning from a batch of BEHAVIOR demos."
        )
        parser.add_argument("--demo_root", type=str, help="Directory containing demos listed in the manifest.")
        parser.add_argument("--log_manifest", type=str, help="Plain text file consisting of list of demos to replay.")
        parser.add_argument("--out_dir", type=str, help="Directory to store results in.")
        parser.add_argument(
            "--config",
            help="which config file to use [default: use yaml files in examples/configs]",
            default=args_dict["config"],
        )

        args = parser.parse_args()
        args_dict["demo_root"] = args.demo_root
        args_dict["log_manifest"] = args.log_manifest
        args_dict["out_dir"] = args.out_dir
        args_dict["config"] = args.config

    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Extract pairs of (observation,action) for imitation learning from a batch of BEHAVIOR demos.
    """
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    generate_il_dataset(args_dict["demo_root"], args_dict["log_manifest"], args_dict["out_dir"], args_dict["config"])


if __name__ == "__main__":
    main()
