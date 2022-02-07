import argparse
import inspect
import json
import logging
import os
import sys

from igibson.envs.igibson_env import iGibsonEnv
from igibson.metrics.agent import RobotMetric
from igibson.metrics.disarrangement import KinematicDisarrangement, LogicalDisarrangement
from igibson.metrics.task import TaskMetric

import behavior.examples


def get_metrics_callbacks(config):
    metrics = [
        KinematicDisarrangement(),
        LogicalDisarrangement(),
        TaskMetric(),
    ]

    robot_type = config["robot"]
    if robot_type == "Fetch" or robot_type == "BehaviorRobot":
        metrics.append(RobotMetric())
    else:
        Exception("Metrics only implemented for Fetch and BehaviorRobot")

    return (
        [metric.start_callback for metric in metrics],
        [metric.step_callback for metric in metrics],
        [metric.end_callback for metric in metrics],
        [metric.gather_results for metric in metrics],
    )


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["config"] = os.path.join(
        os.path.dirname(inspect.getfile(behavior)), "configs", "behavior_full_observability.yaml"
    )
    args_dict["mode"] = "headless"
    args_dict["log_path"] = os.path.join(
        os.path.dirname(inspect.getfile(behavior.examples)), "data", "metrics_log.json"
    )
    if not defaults:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--config",
            "-c",
            default=args_dict["config"],
            help="which config file to use [default: use yaml files in examples/configs]",
        )
        parser.add_argument(
            "--mode",
            "-m",
            choices=["headless", "headless_tensor", "gui_interactive", "gui_non_interactive"],
            default=args_dict["mode"],
            help="which mode for simulation (default: headless)",
        )
        parser.add_argument(
            "--log_path",
            help="where to save the logging results of the metric computation",
        )
        args = parser.parse_args()

        args_dict["config"] = args.config
        args_dict["mode"] = args.mode
        args_dict["log_path"] = args.log_path
    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Compute metrics "live" on a running environment with random actions
    """
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    if headless:
        args_dict["mode"] = "headless"

    logging.info("Create environment")
    env = iGibsonEnv(
        config_file=args_dict["config"],
        mode=args_dict["mode"],
    )

    start_callbacks, step_callbacks, end_callbacks, data_callbacks = get_metrics_callbacks(env.config)

    per_episode_metrics = {}
    for callback in start_callbacks:
        callback(env, None)

    logging.info("Starting metric example")
    num_resets = 10 if not short_exec else 2
    num_steps = (
        1000 if not short_exec else 200
    )  # At least 150 steps to settle the simulator and cache the initial state
    for episode in range(num_resets):
        logging.info("Resetting environment")
        env.reset()
        for i in range(num_steps):
            logging.info("Stepping with random actions")
            action = env.action_space.sample()
            state, reward, done, _ = env.step(action)
            for callback in step_callbacks:
                callback(env, None)
            if done:
                break

        for callback in end_callbacks:
            callback(env, None)

        metrics_summary = {}

        for callback in data_callbacks:
            metrics_summary.update(callback())

        per_episode_metrics[episode] = metrics_summary

    logging.info("Writing metric computation results")
    with open(args_dict["log_path"], "w") as file:
        json.dump(per_episode_metrics, file)

    env.close()


RUN_AS_TEST = True  # Change to True to run this example in test mode
if __name__ == "__main__":
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
