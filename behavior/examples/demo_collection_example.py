"""
Main BEHAVIOR demo collection entrypoint
"""

import argparse
import copy
import datetime
import inspect
import logging
import os
import sys

import bddl
import igibson
import numpy as np
from igibson.envs.igibson_env import iGibsonEnv
from igibson.render.mesh_renderer.mesh_renderer_cpu import MeshRendererSettings
from igibson.render.mesh_renderer.mesh_renderer_vr import VrConditionSwitcher, VrSettings
from igibson.simulator import Simulator
from igibson.simulator_vr import SimulatorVR
from igibson.utils.ig_logging import IGLogWriter
from igibson.utils.utils import parse_config

import behavior

POST_TASK_STEPS = 200
PHYSICS_WARMING_STEPS = 200


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["task"] = "cleaning_windows"
    args_dict["task_id"] = 0
    args_dict["instance_id"] = 0
    args_dict["vr_log_path"] = None  # Internally creates one if we pass None
    args_dict["scene"] = "Rs_int"
    args_dict["disable_save"] = False
    args_dict["disable_scene_cache"] = False
    args_dict["profile"] = False
    args_dict["no_vr"] = True
    args_dict["max_steps"] = -1
    args_dict["config"] = os.path.join(os.path.dirname(inspect.getfile(behavior)), "configs", "behavior_vr.yaml")
    if not defaults:
        scene_choices = [
            "Beechwood_0_int",
            "Beechwood_1_int",
            "Benevolence_0_int",
            "Benevolence_1_int",
            "Benevolence_2_int",
            "Ihlen_0_int",
            "Ihlen_1_int",
            "Merom_0_int",
            "Merom_1_int",
            "Pomaria_0_int",
            "Pomaria_1_int",
            "Pomaria_2_int",
            "Rs_int",
            "Wainscott_0_int",
            "Wainscott_1_int",
        ]

        task_id_choices = [0, 1]
        parser = argparse.ArgumentParser(description="Run and collect a BEHAVIOR demo")
        parser.add_argument(
            "--task",
            type=str,
            required=True,
            nargs="?",
            help="Name of ATUS/BEHAVIOR activity matching parent folder in bddl.",
        )
        parser.add_argument(
            "--task_id",
            type=int,
            required=True,
            choices=task_id_choices,
            nargs="?",
            help="BDDL integer ID for the activity definition, matching suffix of bddl.",
        )
        parser.add_argument(
            "--instance_id",
            type=int,
            required=True,
            help="Instance of behavior activity (particular URDF corresponding to a BDDL file)",
        )
        parser.add_argument("--vr_log_path", type=str, help="Path (and filename) of vr log")
        parser.add_argument(
            "--scene",
            type=str,
            choices=scene_choices,
            nargs="?",
            help="Scene name/ID matching iGibson interactive scenes.",
        )
        parser.add_argument("--disable_save", action="store_true", help="Whether to disable saving logfiles.")
        parser.add_argument(
            "--disable_scene_cache", action="store_true", help="Whether to disable using pre-initialized scene caches."
        )
        parser.add_argument("--profile", action="store_true", help="Whether to print profiling data.")
        parser.add_argument(
            "--no_vr", action="store_true", help="Whether to turn off VR recording and save random actions."
        )
        parser.add_argument(
            "--max_steps",
            type=int,
            default=args_dict["max_steps"],
            help="Maximum number of steps to record before stopping.",
        )
        parser.add_argument(
            "--config",
            help="which config file to use [default: use yaml files in examples/configs]",
            default=args_dict["config"],
        )
        args = parser.parse_args()
        args_dict["task"] = args.task
        args_dict["task_id"] = args.task_id
        args_dict["instance_id"] = args.instance_id
        args_dict["vr_log_path"] = args.vr_log_path
        args_dict["scene"] = args.scene
        args_dict["disable_save"] = args.disable_save
        args_dict["disable_scene_cache"] = args.disable_scene_cache
        args_dict["profile"] = args.profile
        args_dict["no_vr"] = args.no_vr
        args_dict["max_steps"] = args.max_steps
        args_dict["config"] = args.config

    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Example application to collect new demos
    """
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    if short_exec:
        args_dict["max_steps"] = 1000

    collect_demo(
        args_dict["task"],
        args_dict["task_id"],
        args_dict["scene"],
        args_dict["instance_id"],
        args_dict["vr_log_path"],
        args_dict["disable_save"],
        args_dict["max_steps"],
        args_dict["no_vr"],
        args_dict["disable_scene_cache"],
        args_dict["profile"],
        args_dict["config"],
    )


def collect_demo(
    task,
    task_id,
    scene,
    instance_id=0,
    vr_log_path=None,
    disable_save=False,
    max_steps=-1,
    no_vr=False,
    disable_scene_cache=False,
    profile=False,
    config_file=os.path.join(igibson.example_config_path, "behavior_vr.yaml"),
):
    logging.info("Collecting demo")
    # HDR files for PBR rendering
    hdr_texture = os.path.join(igibson.ig_dataset_path, "scenes", "background", "probe_02.hdr")
    hdr_texture2 = os.path.join(igibson.ig_dataset_path, "scenes", "background", "probe_03.hdr")
    light_modulation_map_filename = os.path.join(
        igibson.ig_dataset_path, "scenes", "Rs_int", "layout", "floor_lighttype_0.png"
    )
    background_texture = os.path.join(igibson.ig_dataset_path, "scenes", "background", "urban_street_01.jpg")

    # VR rendering settings
    vr_rendering_settings = MeshRendererSettings(
        optimized=True,
        fullscreen=False,
        env_texture_filename=hdr_texture,
        env_texture_filename2=hdr_texture2,
        env_texture_filename3=background_texture,
        light_modulation_map_filename=light_modulation_map_filename,
        enable_shadow=True,
        enable_pbr=True,
        msaa=False,
        light_dimming_factor=1.0,
    )

    config = parse_config(config_file)
    config["task"] = task
    config["task_id"] = task_id
    config["scene_id"] = scene
    config["instance_id"] = instance_id
    config["online_sampling"] = disable_scene_cache
    config["load_clutter"] = True
    env = iGibsonEnv(
        config_file=config,
        mode="headless" if no_vr else "vr",
        action_timestep=1 / 30.0,
        physics_timestep=1 / 300.0,
        rendering_settings=vr_rendering_settings,
        use_pb_gui=False,
    )
    env.reset()
    vr_agent = env.robots[0]

    if not no_vr:
        env.simulator.register_main_vr_robot(vr_agent)
        vr_cs = VrConditionSwitcher(env.simulator, env.task.show_instruction, env.task.iterate_instruction)
        env.simulator.step_vr_system()

    log_writer = None
    if not disable_save:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if vr_log_path is None:
            vr_log_file = "{}_{}_{}_{}_{}.hdf5".format(task, task_id, scene, instance_id, timestamp)
            vr_log_path = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data", vr_log_file)
        log_writer = IGLogWriter(
            env.simulator,
            log_filepath=vr_log_path,
            task=env.task,
            store_vr=not no_vr,
            vr_robot=vr_agent,
            profiling_mode=profile,
            filter_objects=True,
        )
        log_writer.set_up_data_storage()
        log_writer.hf.attrs["/metadata/instance_id"] = instance_id

    satisfied_predicates_cached = {}

    steps = 0
    steps_after_done = 0

    while True:
        if 0 <= max_steps <= steps:
            break

        if steps_after_done >= POST_TASK_STEPS:
            break

        if no_vr:
            # Use the first 2 steps to activate BehaviorRobot
            if steps < 2:
                # TODO: Check this. Dimensionality correct? Zero action still necessary after Cem's changes?
                action = np.zeros((28,))
                action[19] = 1
                action[27] = 1
            else:
                action = np.random.uniform(-0.01, 0.01, size=(28,))
        else:
            action = env.simulator.gen_vr_robot_action()
            if steps < PHYSICS_WARMING_STEPS:
                action = np.zeros_like(action)

        env.step(action)
        task_done, satisfied_predicates = env.task.check_success()

        if not no_vr:
            if satisfied_predicates != satisfied_predicates_cached:
                vr_cs.refresh_condition(switch=False)
                satisfied_predicates_cached = satisfied_predicates

            if env.simulator.query_vr_event("right_controller", "overlay_toggle"):
                vr_cs.refresh_condition()

            if env.simulator.query_vr_event("left_controller", "overlay_toggle"):
                vr_cs.toggle_show_state()

        if log_writer and not disable_save:
            log_writer.process_frame()

        if task_done:
            steps_after_done += 1
        else:
            # If the task failed again after being successful (e.g. the user knocks off something), reset the counter
            steps_after_done = 0

        steps += 1

    if log_writer and not disable_save:
        log_writer.end_log_session()

    logging.info("End of demo")

    env.close()


if __name__ == "__main__":
    if sys.argv[1] == "--test":
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
