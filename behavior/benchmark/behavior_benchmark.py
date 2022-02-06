import argparse
import json
import logging
import os
import shutil
from collections import defaultdict

import bddl
import igibson
import numpy as np
from igibson.envs.igibson_env import iGibsonEnv
from igibson.metrics.agent import RobotMetric
from igibson.metrics.disarrangement import KinematicDisarrangement, LogicalDisarrangement
from igibson.metrics.task import TaskMetric
from igibson.utils.utils import parse_config

logging.getLogger().setLevel(logging.WARNING)

from behavior.benchmark.agents.random_agent import RandomAgent
from behavior.benchmark.agents.rl_agent import PPOAgent


def get_metrics_callbacks():
    metrics = [
        KinematicDisarrangement(),
        LogicalDisarrangement(),
        RobotMetric(),
        TaskMetric(),
    ]

    return (
        [metric.start_callback for metric in metrics],
        [metric.step_callback for metric in metrics],
        [metric.end_callback for metric in metrics],
        [metric.gather_results for metric in metrics],
    )


class BehaviorBenchmark(object):
    def __init__(self):
        """
        Constructor
        """

    def evaluate_agent(
        self,
        agent,
        env_config_file,
        output_dir,
        tasks,
        scene_instance_ids,
        episodes_per_instance=1,
    ):
        """
        Evaluates the given agent in the activities and instances indicated by the config file and split
        The results are stored in the output directory
        :param agent: Agent to evaluate
        :param env_config: Config file to instantiate the environment (setup, embodiment, sensing, control...)
        :param output_dir: Directory to place the results of the evaluation
        :param tasks: Tasks to evaluate
        :param scene_instance_ids: Dictionary of scenes and instances per scene to perform evaluation
        :param episodes_per_instance: Number of episodes to evaluate the agent in the same conditions
        :return:
        """
        env_config = parse_config(env_config_file)

        log_path = os.path.join(output_dir, "per_episode_metrics.json")
        summary_log_path = os.path.join(output_dir, "aggregated_metrics.json")

        self_reported_log_path = os.path.join(
            output_dir, "..", "participant_reported_results", "per_episode_metrics.json"
        )
        self_reported_summary_log_path = os.path.join(
            output_dir, "..", "participant_reported_results", "aggregated_metrics.json"
        )
        if os.path.exists(self_reported_log_path):
            shutil.copyfile(self_reported_log_path, log_path)
            print("Per episode eval results copied from self-reported results %s" % log_path)
            with open(self_reported_log_path) as f:
                self_reported_log = json.load(f)
                assert len(self_reported_log) == len(tasks) * 9

        if os.path.exists(self_reported_summary_log_path):
            shutil.copyfile(self_reported_summary_log_path, summary_log_path)
            print("Aggregated eval results copied from self-reported results %s" % summary_log_path)
            return

        # Evaluation ##################################################################################################
        episode = 0
        per_episode_metrics = {}

        # This provides metadata about the activities, including the time humans require to perform them
        with open(os.path.join(igibson.ig_dataset_path, "metadata", "behavior_activity_statistics.json")) as f:
            activity_metadata = json.load(f)

        for task in tasks:
            human_demo_mean_step = activity_metadata[task]["mean"]  # Mean time invested by humans in the task
            print("Maximum number of steps is twice the mean of human time: {}".format(human_demo_mean_step * 2))
            env_config["max_step"] = human_demo_mean_step * 2  # adjust env_config['max_step'] based on the human
            # demonstration, we give agent 2x steps of average human demonstration across all possible scenes

            for scene_id, instance_ids in scene_instance_ids.items():
                env_config["scene_id"] = scene_id
                env_config["task"] = task
                env_config["task_id"] = 0
                for instance_id in instance_ids:
                    for episode_id in range(episodes_per_instance):
                        print(
                            "New episode: task {}, scene {}, instance {}, episode {}".format(
                                task, scene_id, instance_id, episode_id
                            )
                        )
                        env_config["instance_id"] = instance_id
                        env = iGibsonEnv(
                            config_file=env_config,
                            mode="headless",
                            action_timestep=1.0 / 30.0,
                            physics_timestep=1.0 / 120.0,
                        )
                        (
                            start_callbacks,
                            step_callbacks,
                            end_callbacks,
                            data_callbacks,
                        ) = get_metrics_callbacks()
                        for callback in start_callbacks:
                            callback(env.task, None)
                        agent.reset()
                        state = env.reset()
                        while True:
                            action = agent.act(state)
                            state, reward, done, info = env.step(action)
                            for callback in step_callbacks:
                                callback(env.task, None)
                            if done:
                                break
                        for callback in end_callbacks:
                            callback(env.task, None)
                        metrics_summary = {}
                        for callback in data_callbacks:
                            print("Generating report for the episode")
                            metrics_summary.update(callback())

                        metrics_summary["task"] = task
                        per_episode_metrics[episode] = metrics_summary
                        episode += 1
                        env.close()

        with open(log_path, "w+") as f:
            json.dump(per_episode_metrics, f)
        print("Per episode eval results saved to %s" % log_path)

        aggregated_metrics = {}
        success_score = []
        simulator_time = []
        kinematic_disarrangement = []
        logical_disarrangement = []
        distance_navigated = []
        displacement_of_hands = []

        task_to_mean_success_score = defaultdict(list)
        task_scores = []

        for episode, metric in per_episode_metrics.items():
            task_to_mean_success_score[metric["task"]].append(metric["q_score"]["final"])

        for task, scores in task_to_mean_success_score.items():
            task_scores.append(np.mean(scores))

        task_scores = sorted(task_scores, reverse=True)

        for episode, metric in per_episode_metrics.items():
            success_score.append(metric["q_score"]["final"])
            simulator_time.append(metric["time"]["simulator_time"])
            kinematic_disarrangement.append(metric["kinematic_disarrangement"]["relative"])
            logical_disarrangement.append(metric["logical_disarrangement"]["relative"])
            distance_navigated.append(np.sum(metric["agent_distance"]["timestep"]["body"]))
            displacement_of_hands.append(
                np.sum(metric["grasp_distance"]["timestep"]["left_hand"])
                + np.sum(metric["grasp_distance"]["timestep"]["right_hand"])
            )

        aggregated_metrics["Success Score"] = np.mean(success_score)
        aggregated_metrics["Success Score Top 5"] = np.mean(np.array(task_scores)[:5])
        aggregated_metrics["Simulated Time"] = np.mean(simulator_time)
        aggregated_metrics["Kinematic Disarrangement"] = np.mean(kinematic_disarrangement)
        aggregated_metrics["Logical Disarrangement"] = np.mean(logical_disarrangement)
        aggregated_metrics["Distance Navigated"] = np.mean(distance_navigated)
        aggregated_metrics["Displacement of Hands"] = np.mean(displacement_of_hands)
        with open(summary_log_path, "w+") as f:
            json.dump(aggregated_metrics, f)
        print("Aggregated eval results saved to %s" % summary_log_path)

    def benchmark_agent(self, agent, env_config_file="", output_dir="", split=""):
        """
        Benchmark the agent following the official guidelines:
        - All activities or the ones specified in the split
        - Nine episodes, one per activity instance:
            - Three activity instances with "seen" object poses, objects, furniture and scene/home
            - Three activity instances with "unseen" object poses, "seen" objects, furniture and scene/home
            - Three activity instances with "unseen" object poses, "seen" objects, "unseen" furniture, "seen" scene
        :param agent: Agent to evaluate
        :return:
        """
        # Takes variables set as environment variables or passed as params in initialization
        if env_config_file == "":
            print("Environment's config file is not an argument. Obtaining it from the environmental variables.")
            env_config_file = os.environ["CONFIG_FILE"]

        print("Using environment's config file: " + env_config_file)

        if output_dir == "":
            print("Output directory is not an argument. Obtaining it from the environmental variables.")
            output_dir = os.environ["OUTPUT_DIR"]

        print("Using output dir: " + output_dir)

        if split == "":
            print("Split is not an argument. Obtaining it from the environmental variables.")
            split = os.environ["SPLIT"]
            print("Using split: " + split)

        # Get list of all 100 activities
        tasks = sorted(
            [
                item
                for item in os.listdir(os.path.join(os.path.dirname(bddl.__file__), "activity_definitions"))
                if item != "domain_igibson.bddl"
            ]
        )
        assert len(tasks) == 100
        if split == "minival":
            # Only evaluate a single activity specified in the config file, pass an empty list
            # If the input tasks is an empty list, we take the task from the config file
            if len(tasks) == 0:
                env_config = parse_config(env_config_file)
                tasks = [env_config["task"]]
            print("Evaluating agent on activity {}".format(tasks[0]))
        elif split in tasks:
            # Only evaluate a single activity specified by name
            tasks = [split]
            print("Evaluating agent on activity {}".format(tasks[0]))
        elif all(elem in tasks for elem in split):
            # Split is a list of valid tasks
            tasks = split
            print("Evaluating agent on activities {}".format(tasks))
        elif self.split in ["dev", "test"]:
            # Evaluate all activities
            print("Evaluating agent on all activities")

        # This provides a dictionary of scenes where each activity can be successfully performed
        scene_json = os.path.join(
            os.path.dirname(bddl.__file__),
            "../utils",
            "activity_to_preselected_scenes.json",
        )
        with open(scene_json) as f:
            activity_to_scenes = json.load(f)

        for task in tasks:
            assert task in activity_to_scenes.keys()
            scenes = sorted(set(activity_to_scenes[task]))  # Scenes where the activity can be performed
            num_scenes = len(scenes)
            assert num_scenes <= 3
            # Official benchmark: Evaluate 9 episodes per task
            # instance id 0-9: seen poses
            # instance id 10-19: unseen poses
            # instance id 20-29: unseen scenes (same houses but different furniture arrangement)
            # If you don't have enough task instances in ig_dataset, the behavior data bundle is outdated.
            # You need to follow the participant guide and download again.

            if num_scenes == 3:
                # Regular case. We use three instances per scene (one "seen poses", one "unseen poses" and one
                # "unseen scene" (different furniture))
                scene_instance_ids = {
                    scenes[0]: [0, 10, 20],
                    scenes[1]: [0, 10, 20],
                    scenes[2]: [0, 10, 20],
                }
            elif num_scenes == 2:
                # We use four instances of one scene (two "seen poses", one "unseen poses" and one
                # "unseen scene" (different furniture)) and five from another scene (two "seen poses", two
                # "unseen poses" and one "unseen scene" (different furniture))
                scene_instance_ids = {
                    scenes[0]: [0, 1, 10, 20],
                    scenes[1]: [0, 1, 10, 11, 20],
                }
            else:
                # We use nine instances of one scene (three "seen poses", three "unseen poses" and three
                # "unseen scene" (different furniture))
                scene_instance_ids = {scenes[0]: [0, 1, 2, 10, 11, 12, 20, 21, 22]}

            self.evaluate_agent(agent, env_config_file, output_dir, tasks, scene_instance_ids)


def get_agent(agent_class, ckpt_path=""):
    if agent_class == "Random":
        return RandomAgent()
    elif agent_class == "PPO":
        return PPOAgent(ckpt_path)
    else:
        print("Agent class not recognize. Consider adding it.")
        exit(-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-class", type=str, default="Random", choices=["Random", "PPO"])
    parser.add_argument("--ckpt-path", default="", type=str)
    parser.add_argument("--split", default="minival", type=str)

    args = parser.parse_args()

    print("Evaluating agent of type {} on split {}".format(args.agent_class, args.split))

    agent = get_agent(agent_class=args.agent_class, ckpt_path=args.ckpt_path)
    challenge = BehaviorBenchmark()
    challenge.benchmark_agent(agent, split=args.split)


if __name__ == "__main__":
    main()
