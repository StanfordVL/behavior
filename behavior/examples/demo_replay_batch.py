"""
BEHAVIOR demo batch analysis script
"""
import argparse
import inspect
import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd

import behavior
from behavior.examples.demo_replay_example import replay_demo


def replay_demo_batch(
    demo_root,
    log_manifest,
    out_dir,
    get_callbacks_callback,
    skip_existing=True,
    ignore_errors=True,
    save_frames=False,
    debug_display=False,
    image_size=(1280, 720),
    deactivate_logger=True,
):
    """
    Execute replay analysis functions (provided through callbacks) on a batch of BEHAVIOR demos.

    @param demo_root: Directory containing the demo files listed in the manifests.
    @param log_manifest: The manifest file containing list of BEHAVIOR demos to batch over.
    @param out_dir: Directory to store results in.
    @param get_callbacks_callback: A function that will be called for each demo that needs to return
        a four-tuple: (start_callbacks, step_callbacks, end_callbacks, data_callbacks). Each of the
        the first three callback function sets need to be compatible with the behavior_demo_replay
        API and will be used for this purpose for that particular demo. The data callbacks should
        take no arguments and return a dictionary to be included in the demo's replay data that will
        be saved in the end.
    @param ignore_errors: If an Error is raised, the batch will continue if this is True (with the error saved to the
        log file). If False, the error will be propagated.
    @param skip_existing: Whether demos with existing output logs should be skipped.
    @param save_frames: Whether the demo's frames should be saved alongside statistics.
    @param debug_display: Whether a debug display (the pybullet GUI) should be enabled.
    @param image_size: The image size that should be used by the renderer.
    @param deactivate_logger: If we deactivate the logger
    """

    if deactivate_logger:
        logger = logging.getLogger()
        logger.disabled = True

    demo_list = pd.read_csv(log_manifest)

    logging.info("Demos in manifest: {}".format(demo_list["demos"]))

    for idx, demo in enumerate(demo_list["demos"]):
        if "replay" in demo:
            continue

        demo_name = os.path.splitext(demo)[0]
        demo_path = os.path.join(demo_root, demo)
        replay_path = os.path.join(out_dir, demo_name + "_replay.hdf5")
        log_path = os.path.join(out_dir, demo_name + "_replay_log.json")

        if skip_existing and os.path.exists(log_path):
            logging.info("Skipping existing demo: {}, {} out of {}".format(demo, idx, len(demo_list["demos"])))
            continue

        logging.info("Replaying demo: {}, {} out of {}".format(demo, idx, len(demo_list["demos"])))

        curr_frame_save_path = None
        if save_frames:
            curr_frame_save_path = os.path.join(out_dir, demo_name + ".mp4")

        try:
            if get_callbacks_callback is not None:
                start_callbacks, step_callbacks, end_callbacks, data_callbacks = get_callbacks_callback(
                    demo_name=demo_name, out_dir=out_dir
                )
            else:
                start_callbacks, step_callbacks, end_callbacks, data_callbacks = [], [], [], []
            demo_information = replay_demo(
                in_log_path=demo_path,
                out_log_path=replay_path,
                frame_save_path=curr_frame_save_path,
                start_callbacks=start_callbacks,
                step_callbacks=step_callbacks,
                end_callbacks=end_callbacks,
                mode="headless",
                use_pb_gui=debug_display,
                verbose=False,
                image_size=image_size,
            )
            demo_information["failed"] = False
            demo_information["filename"] = Path(demo).name

            for callback in data_callbacks:
                demo_information.update(callback())

        except Exception as e:
            if ignore_errors:
                logging.info("Demo failed with the error: {}".format(str(e)))
                demo_information = {"demo_id": Path(demo).name, "failed": True, "failure_reason": str(e)}
            else:
                raise

        with open(log_path, "w") as file:
            json.dump(demo_information, file)


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_root"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["log_manifest"] = os.path.join(
        os.path.dirname(inspect.getfile(behavior.examples)), "data", "test_manifest.txt"
    )
    args_dict["out_dir"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["split"] = 0
    if not defaults:
        parser = argparse.ArgumentParser(description="Replays a batch demos specified in a manifest file")
        parser.add_argument(
            "--demo_root", type=str, required=True, help="Directory containing the demo files listed in the manifests."
        )
        parser.add_argument(
            "--log_manifest",
            type=str,
            required=True,
            help="The manifest file containing list of BEHAVIOR demos to batch over.",
        )
        parser.add_argument("--demo_root", type=str, required=True, help="Directory to store results in.")
        args = parser.parse_args()
        args_dict["demo_root"] = args.demo_root
        args_dict["log_manifest"] = args.log_manifest
        args_dict["out_dir"] = args.out_dir
    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Replays a batch of demos specified in a manifest file
    """
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    get_callbacks_callback = None  # Add a function that generates callbacks here to call during the batch processing
    replay_demo_batch(
        args_dict["demo_root"],
        args_dict["log_manifest"],
        args_dict["out_dir"],
        get_callbacks_callback,
        deactivate_logger=False,
        skip_existing=not defaults,  # Do not skip when testing
    )


if __name__ == "__main__":
    if sys.argv[1] == "--test":
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
