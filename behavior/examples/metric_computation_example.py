import argparse
import logging
import json
import os

from igibson.envs.igibson_env import iGibsonEnv
from igibson.metrics.agent import RobotMetric
from igibson.metrics.disarrangement import KinematicDisarrangement, LogicalDisarrangement
from igibson.metrics.task import TaskMetric

import behavior


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
    args_dict["config"] = os.path.join(behavior.configs_path, "behavior_full_observability.yaml")
    args_dict["mode"] = "headless"
    args_dict["out_metric_log_file"] = os.path.join(behavior.examples_path, "data", "metrics_log.json")
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
            "--out_metric_log_file",
            help="where to save the logging results of the metric computation",
        )
        args = parser.parse_args()

        args_dict["config"] = args.config
        args_dict["mode"] = args.mode
        args_dict["out_metric_log_file"] = args.out_metric_log_file
    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Compute metrics "live" on a running environment with random actions
    """

    print("*" * 80 + "\nDescription:" + main.__doc__ + "\n" + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    if headless:
        args_dict["mode"] = "headless"

    print("Create environment")
    env = iGibsonEnv(
        config_file=args_dict["config"],
        mode=args_dict["mode"],
    )

    start_callbacks, step_callbacks, end_callbacks, data_callbacks = get_metrics_callbacks(env.config)

    per_episode_metrics = {}
    for callback in start_callbacks:
        callback(env, None)

    print("Starting metric example")
    num_resets = 10 if not short_exec else 2
    num_steps = (
        1000 if not short_exec else 200
    )  # At least 150 steps to settle the simulator and cache the initial state
    for episode in range(num_resets):
        print("Resetting environment")
        env.reset()
        for i in range(num_steps):
            print("Stepping with random actions")
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

    print("Writing metric computation results")
    with open(args_dict["out_metric_log_file"], "w") as file:
        json.dump(per_episode_metrics, file)

    env.close()


RUN_AS_TEST = False  # Change to True to run this example in test mode
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
