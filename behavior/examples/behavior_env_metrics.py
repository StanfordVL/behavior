import argparse
import json
import os
import parser

import bddl
import igibson
from igibson.envs.igibson_env import iGibsonEnv
from igibson.metrics.agent import RobotMetric
from igibson.metrics.disarrangement import KinematicDisarrangement, LogicalDisarrangement
from igibson.metrics.task import TaskMetric


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
    default_config = "behavior_full_observability.yaml"
    default_mode = "headless"
    args_dict = dict()
    if not defaults:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--config",
            "-c",
            default=os.path.join(igibson.example_config_path, default_config),
            help="which config file to use [default: use yaml files in examples/configs]",
        )
        parser.add_argument(
            "--mode",
            "-m",
            choices=["headless", "headless_tensor", "gui_interactive", "gui_non_interactive"],
            default=default_mode,
            help="which mode for simulation (default: headless)",
        )
        args = parser.parse_args()

    args_dict["config"] = default_config if defaults else args.config
    args_dict["mode"] = default_mode if defaults else args.mode
    return args_dict


def main(selection="user", headless=False, short_exec=False):

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    if headless:
        args_dict["mode"] = "headless"

    env = iGibsonEnv(
        config_file=args_dict["config"],
        mode=args_dict["mode"],
    )

    start_callbacks, step_callbacks, end_callbacks, data_callbacks = get_metrics_callbacks(env.config)

    per_episode_metrics = {}
    for callback in start_callbacks:
        callback(env, None)

    num_resets = 10 if not short_exec else 2
    num_steps = 1000 if not short_exec else 10
    for episode in range(num_resets):
        env.reset()
        for i in range(num_steps):
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

    log_path = "my_igibson_run.json"

    with open(log_path, "w") as file:
        json.dump(per_episode_metrics, file)

    env.close()


if __name__ == "__main__":
    main()
