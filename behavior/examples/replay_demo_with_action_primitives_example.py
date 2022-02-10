import argparse
import inspect
import json
import logging
import os
import sys
import time

import igibson
import yaml
from igibson.envs.behavior_mp_env import ActionPrimitives, BehaviorMPEnv
from igibson.utils.ig_logging import IGLogReader

import behavior
import behavior.examples


def get_empty_hand(current_hands):
    if len(current_hands) == 0:
        return "right_hand"
    elif len(current_hands) == 1:
        return "left_hand" if list(current_hands.values())[0] == "right_hand" else "right_hand"

    raise ValueError("Both hands are full but you are trying to execute a grasp.")


def get_actions_from_segmentation(demo_data):
    logging.info("Conversion of demo segmentation to action primitives:")

    hand_by_object = {}
    actions = []
    segmentation = demo_data["segmentations"]["flat"]["sub_segments"]

    # Convert the segmentation to a sequence of state changes.
    state_changes = []
    for segment in segmentation:
        state_records = segment["state_records"]
        if len(state_records) == 0:
            logging.info("Found segment with no useful state changes: {}".format(segment))
            continue
        elif len(state_records) > 1:
            logging.info("Found segment with multiple state changes, using the first: {}".format(segment))

        state_change = state_records[0]
        state_changes.append(state_change)

    # Now go through the state changes and convert them to actions
    for i, state_change in enumerate(state_changes):
        # Handle the combinations that we support.
        state_name = state_change["name"]
        state_value = state_change["value"]

        # TODO(replayMP): Here we compute grasps based on the InHand state. Ditch this and simply do a single-hand
        # grasp on the object we will manipulate next. That way it will be fetch-compatible.
        if state_name == "Open" and state_value is True:
            primitive = ActionPrimitives.OPEN
            target_object = state_change["objects"][0]
        elif state_name == "Open" and state_value is False:
            primitive = ActionPrimitives.CLOSE
            target_object = state_change["objects"][0]
        elif state_name == "InReachOfRobot" and state_value is True:
            # The primitives support automatic navigation to relevant objects.
            continue
        elif state_name == "InHandOfRobot" and state_value is True:
            target_object = state_change["objects"][0]

            # Check that we do something with this object later on, otherwise don't grasp it.
            is_used = False
            for future_state_change in state_changes[i + 1 :]:
                # We should only grasp the moved object in these cases.
                if future_state_change["objects"][0] != target_object:
                    continue

                if future_state_change["name"] == "InHandOfRobot" and future_state_change["value"] is True:
                    # This object is re-grasped later. No need to look any further than that.
                    break

                # We only care about Inside and OnTop use cases later.
                if future_state_change["name"] not in ("Inside", "OnTop") or future_state_change["value"] is False:
                    continue

                # This is a supported use case so we approve the grasp.
                is_used = True
                break

            # If the object is not used in the future, don't grasp it.
            if not is_used:
                continue

            hand = get_empty_hand(hand_by_object)
            hand_by_object[target_object] = hand
            primitive = ActionPrimitives.LEFT_GRASP if hand == "left_hand" else ActionPrimitives.RIGHT_GRASP
        elif state_name == "Inside" and state_value is True:
            placed_object = state_change["objects"][0]
            target_object = state_change["objects"][1]
            if placed_object not in hand_by_object:
                logging.info(
                    "Placed object %s in segment %d not currently grasped. Maybe some sort of segmentation error?".format(
                        placed_object, i
                    )
                )
                continue
            hand = hand_by_object[placed_object]
            del hand_by_object[placed_object]
            primitive = (
                ActionPrimitives.LEFT_PLACE_INSIDE if hand == "left_hand" else ActionPrimitives.RIGHT_PLACE_INSIDE
            )
        elif state_name == "OnTop" and state_value is True:
            placed_object = state_change["objects"][0]
            target_object = state_change["objects"][1]
            if placed_object not in hand_by_object:
                logging.info(
                    "Placed object %s in segment %d not currently grasped. Maybe some sort of segmentation error?".format(
                        placed_object, i
                    )
                )
                continue
            hand = hand_by_object[placed_object]
            del hand_by_object[placed_object]
            primitive = ActionPrimitives.LEFT_PLACE_ONTOP if hand == "left_hand" else ActionPrimitives.RIGHT_PLACE_ONTOP
        else:
            raise ValueError("Found a state change we can't process: %r" % state_change)

        # Append the action.
        action = (primitive, target_object)
        actions.append(action)
        logging.info("Action: {}".format(action))

    logging.info("Conversion completed")
    return actions


def replay_demo_with_aps(demo_file, segm_file, ap_replay_demo_file, config_file):
    task = IGLogReader.read_metadata_attr(demo_file, "/metadata/atus_activity")
    task_id = IGLogReader.read_metadata_attr(demo_file, "/metadata/activity_definition")
    scene_id = IGLogReader.read_metadata_attr(demo_file, "/metadata/scene_id")

    # Load the segmentation of a demo for this task.
    with open(segm_file, "r") as f:
        selected_demo_data = json.load(f)

    # Get the actions from the segmentation
    actions = get_actions_from_segmentation(selected_demo_data)

    # Prepare the environment
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    config["task"] = task
    config["task_id"] = task_id
    config["scene_id"] = scene_id

    env = BehaviorMPEnv(
        config_file=config,
        mode="headless",
        action_timestep=1.0 / 300.0,
        physics_timestep=1.0 / 300.0,
        use_motion_planning=False,
        activity_relevant_objects_only=False,
    )

    start = time.time()
    env.reset()

    # env.robots[0].set_position_orientation([0, 0, 0.7], [0, 0, 0, 1])
    done = False
    infos = []
    action_successes = []
    import pybullet as p

    p.configureDebugVisualizer(p.COV_ENABLE_GUI, False)
    p.resetDebugVisualizerCamera(cameraTargetPosition=[1, -1, 0], cameraDistance=4, cameraYaw=240, cameraPitch=-45)
    for action_pair in actions:
        # try:
        logging.info("Executing {}".format(action_pair))
        primitive, obj_name = action_pair

        # Convert the action
        obj_id = next(i for i, obj in enumerate(env.addressable_objects) if obj.name == obj_name)
        action = int(primitive) * env.num_objects + obj_id

        # Execute.
        state, reward, done, info = env.step(action)
        logging.info("Reward: {}, Info: {}".format(reward, info))
        infos.append(info)
        action_successes.append(True)
        if done:
            break
        # except:
        #     action_successes.append(False)

    # Dump the results
    data = {"actions": actions, "infos": infos, "action_successes": action_successes}
    with open(ap_replay_demo_file, "w") as f:
        json.dump(data, f)

    logging.info(
        "Episode finished after {} timesteps, took {} seconds. Done: {}".format(
            env.current_step, time.time() - start, done
        )
    )
    env.close()


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_file"] = os.path.join(
        igibson.ig_dataset_path,
        "tests",
        "cleaning_windows_0_Rs_int_2021-05-23_23-11-46.hdf5",
    )
    args_dict["segm_file"] = os.path.join(
        os.path.dirname(inspect.getfile(behavior.examples)),
        "data",
        "test_segm.json",
    )
    args_dict["ap_replay_demo_file"] = os.path.splitext(args_dict["demo_file"])[0] + "_ap_replay.json"

    # Todo: maybe better behavior_vr.yaml?
    args_dict["config"] = os.path.join(
        os.path.dirname(inspect.getfile(behavior)), "configs", "behavior_full_observability.yaml"
    )

    if not defaults:
        parser = argparse.ArgumentParser()
        parser.add_argument("demo_file", type=str, help="Path of the demo hdf5 to replay.")
        parser.add_argument("segm_file", type=str, help="Path of the segmentation of the demo.")
        parser.add_argument("ap_replay_demo_file", type=str, help="Path to output result JSON file to.")
        parser.add_argument("--config", help="which config file to use [default: use yaml files in examples/configs]")
        args = parser.parse_args()
        args_dict["demo_file"] = args.demo_file
        args_dict["segm_file"] = args.segm_file
        args_dict["ap_replay_demo_file"] = args.ap_replay_demo_file
        args_dict["config"] = args.config

    return args_dict


def main(selection="user", headless=False, short_exec=False):
    """
    Replays a demo using action primitives
    The demo must be segmented before into a valid sequence of action primitives
    """
    logging.getLogger().setLevel(logging.INFO)
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    replay_demo_with_aps(
        args_dict["demo_file"], args_dict["segm_file"], args_dict["ap_replay_demo_file"], args_dict["config"]
    )


RUN_AS_TEST = False  # Change to True to run this example in test mode
if __name__ == "__main__":
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
