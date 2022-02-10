import argparse
import inspect
import json
import logging
import os
from collections import deque, namedtuple
from enum import Enum

import igibson
import printree
import pyinstrument
from igibson import object_states
from igibson.examples.learning import demo_replaying_example
from igibson.object_states import ROOM_STATES, factory
from igibson.object_states.object_state_base import AbsoluteObjectState, BooleanState, RelativeObjectState
from igibson.robots.behavior_robot import BRBody
from igibson.tasks.bddl_backend import ObjectStateBinaryPredicate, ObjectStateUnaryPredicate

import behavior.examples

StateRecord = namedtuple("StateRecord", ["state_type", "objects", "value"])
StateEntry = namedtuple("StateEntry", ["frame_count", "state_records"])
Segment = namedtuple("DiffEntry", ["start", "duration", "end", "state_records", "sub_segments"])


class SegmentationObjectSelection(Enum):
    ALL_OBJECTS = 1
    TASK_RELEVANT_OBJECTS = 2
    ROBOTS = 3


class SegmentationStateSelection(Enum):
    ALL_STATES = 1
    GOAL_CONDITION_RELEVANT_STATES = 2


class SegmentationStateDirection(Enum):
    BOTH_DIRECTIONS = 1
    FALSE_TO_TRUE = 2
    TRUE_TO_FALSE = 3


STATE_DIRECTIONS = {
    # Note that some of these states already only go False-to-True so they are left as BOTH_DIRECTIONS
    # so as not to add filtering work.
    object_states.Burnt: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.Cooked: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.Dusty: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.Frozen: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.InFOVOfRobot: SegmentationStateDirection.FALSE_TO_TRUE,
    object_states.InHandOfRobot: SegmentationStateDirection.FALSE_TO_TRUE,
    object_states.InReachOfRobot: SegmentationStateDirection.FALSE_TO_TRUE,
    object_states.InSameRoomAsRobot: SegmentationStateDirection.FALSE_TO_TRUE,
    object_states.Inside: SegmentationStateDirection.FALSE_TO_TRUE,
    object_states.NextTo: SegmentationStateDirection.FALSE_TO_TRUE,
    # OnFloor: SegmentationStateDirection.FALSE_TO_TRUE,
    object_states.OnTop: SegmentationStateDirection.FALSE_TO_TRUE,
    object_states.Open: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.Sliced: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.Soaked: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.Stained: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.ToggledOn: SegmentationStateDirection.BOTH_DIRECTIONS,
    # Touching: SegmentationStateDirection.BOTH_DIRECTIONS,
    object_states.Under: SegmentationStateDirection.FALSE_TO_TRUE,
}
STATE_DIRECTIONS.update({state: SegmentationStateDirection.FALSE_TO_TRUE for state in ROOM_STATES})

ALLOWED_SUB_SEGMENTS_BY_STATE = {
    object_states.Burnt: {object_states.OnTop, object_states.ToggledOn, object_states.Open, object_states.Inside},
    object_states.Cooked: {object_states.OnTop, object_states.ToggledOn, object_states.Open, object_states.Inside},
    object_states.Dusty: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot, object_states.InHandOfRobot},
    object_states.Frozen: {
        object_states.InReachOfRobot,
        object_states.OnTop,
        object_states.ToggledOn,
        object_states.Open,
        object_states.Inside,
    },
    object_states.InFOVOfRobot: {},
    object_states.InHandOfRobot: {},
    object_states.InReachOfRobot: {},
    object_states.InSameRoomAsRobot: {},
    object_states.Inside: {
        object_states.Open,
        object_states.InSameRoomAsRobot,
        object_states.InReachOfRobot,
        object_states.InHandOfRobot,
    },
    object_states.NextTo: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot, object_states.InHandOfRobot},
    # OnFloor: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot, object_states.InHandOfRobot},
    object_states.OnTop: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot, object_states.InHandOfRobot},
    object_states.Open: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot, object_states.InHandOfRobot},
    object_states.Sliced: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot, object_states.InHandOfRobot},
    object_states.Soaked: {
        object_states.ToggledOn,
        object_states.InSameRoomAsRobot,
        object_states.InReachOfRobot,
        object_states.InHandOfRobot,
    },
    object_states.Stained: {
        object_states.Soaked,
        object_states.InSameRoomAsRobot,
        object_states.InReachOfRobot,
        object_states.InHandOfRobot,
    },
    object_states.ToggledOn: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot},
    # Touching: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot, object_states.InHandOfRobot},
    object_states.Under: {object_states.InSameRoomAsRobot, object_states.InReachOfRobot, object_states.InHandOfRobot},
}


def process_states(objects, state_types):
    """
    Process/Analyze the state of the relevant objects for the segmentation
    :param objects: Objects to analyze for the segmentation
    :param state_types: State types to analyze for the segmentation
    :return: Set of predicates in the form of StateRecords that contain the type of state, the object(s) involved and the value of the state
    """
    predicate_states = set()

    for obj in objects:
        for state_type in state_types:

            # If this type of state does not apply to this object (e.g., frozen for a table)
            if state_type not in obj.states:
                continue

            # For some reason, the state types have to be all Booleans
            assert issubclass(state_type, BooleanState)

            # Get the state of this state type
            state = obj.states[state_type]
            if issubclass(state_type, AbsoluteObjectState):
                # Add only one instance of absolute state
                try:
                    value = bool(state.get_value())
                    record = StateRecord(state_type, (obj,), value)
                    predicate_states.add(record)
                except ValueError:
                    pass
            elif issubclass(state_type, RelativeObjectState):
                # Add one instance per state pair
                for other in objects:
                    try:
                        value = state.get_value(other)
                        record = StateRecord(state_type, (obj, other), value)
                        predicate_states.add(record)
                    except ValueError:
                        pass
            else:
                raise ValueError("Unusable state for segmentation.")

    return predicate_states


def _get_goal_condition_states(env):
    state_types = set()

    q = deque()
    q.extend(env.task.goal_conditions)

    while q:
        pred = q.popleft()
        if isinstance(pred, ObjectStateUnaryPredicate) or isinstance(pred, ObjectStateBinaryPredicate):
            state_types.add(pred.STATE_CLASS)

        q.extend(pred.children)

    return state_types


class DemoSegmentationProcessor(object):
    """
    Processing object for demos that segments them
    """

    def __init__(
        self,
        state_types=None,
        object_selection=SegmentationObjectSelection.TASK_RELEVANT_OBJECTS,
        label_by_instance=False,
        hierarchical=False,
        diff_initial=False,
        state_directions=STATE_DIRECTIONS,
        profiler=None,
    ):
        # List of StateEntry's
        self.state_history = []
        self.last_state = None

        # List of state types to use for segmentation
        self.state_types_option = state_types

        # To be populated in initialize(). It will contain the types of states to track for segmenting
        self.state_types = None

        # Direction we want states to change, e.g., from True to False or vice versa.
        # For different state types can be different
        self.state_directions = state_directions

        # Objects to analyze for the segmentation (e.g., task relevant or all)
        self.object_selection = object_selection
        self.label_by_instance = label_by_instance

        self.hierarchical = hierarchical
        self.all_state_types = None

        # We save a first empty StateEntry that works as initial one for doing diff
        if diff_initial:
            self.state_history.append(StateEntry(0, set()))
            self.last_state = set()

        self.profiler = profiler

    def start_callback(self, env, _):
        """
        Initial callback to call at the beginning of the segmentation process.
        It populates state_types, the types of states to listen to in order to segment the demos.
        :param env: Environment to evaluate
        :param _: ?
        :return: None
        """
        self.all_state_types = [
            state
            for state in factory.get_all_states()
            if (
                issubclass(state, BooleanState)
                and (issubclass(state, AbsoluteObjectState) or issubclass(state, RelativeObjectState))
            )
        ]  # All the state types we use for segmentation

        if isinstance(self.state_types_option, list) or isinstance(self.state_types_option, set):
            self.state_types = self.state_types_option
        elif self.state_types_option == SegmentationStateSelection.ALL_STATES:
            self.state_types = self.all_state_types
        elif self.state_types_option == SegmentationStateSelection.GOAL_CONDITION_RELEVANT_STATES:
            self.state_types = _get_goal_condition_states(env)
        else:
            raise ValueError("Unknown segmentation state selection.")

        if self.state_types is None:
            from IPython import embed

            embed()

    def step_callback(self, env, _):
        """
        Callback to call at each step of the segmentation process.
        :param env:
        :param _:
        :return: None
        """
        if self.profiler:
            self.profiler.start()

        # Get the objects to analyze for the segmentation based on the object_selection
        if self.object_selection == SegmentationObjectSelection.TASK_RELEVANT_OBJECTS:
            objects = [obj for obj in env.task.object_scope.values() if not isinstance(obj, BRBody)]
        elif self.object_selection == SegmentationObjectSelection.ROBOTS:
            objects = [obj for obj in env.task.object_scope.values() if isinstance(obj, BRBody)]
        elif self.object_selection == SegmentationObjectSelection.ALL_OBJECTS:
            objects = env.scene.get_objects()
        else:
            raise ValueError("Incorrect SegmentationObjectSelection %r" % self.object_selection)

        # Get the processed state -> states of the state types indicated for the objects indicated
        state_types_to_use = self.state_types if not self.hierarchical else self.all_state_types
        processed_state = process_states(objects, state_types_to_use)
        # If this is the first step (last_state is None) or there is a change in the logic states ("-" between
        # sets returns the non-common entries), we add this processed state to the history
        if self.last_state is None or (processed_state - self.last_state):
            self.state_history.append(StateEntry(env.simulator.frame_count, processed_state))

        self.last_state = processed_state

        if self.profiler:
            self.profiler.stop()

    def obj2str(self, obj):
        return obj.name if self.label_by_instance else obj.category

    def _hierarchical_segments(self, state_entries, state_types):
        """
        Create a "hierarchical" list of segments: segments followed by subsegments
        So far we only have flat segmentations, so there won't be much recursion, but this function is recursive
        :param state_entries: History of states for the relevant objects
        :param state_types: State types to analyze for the segmentation
        :return:
        """
        if not state_types:
            logging.info("No state_types. Returning empty list")
            return []

        segments = []
        before_idx = 0
        after_idx = 1

        # Keep iterating until we reach the end of our state entries.
        while after_idx < len(state_entries):
            # Get the state entries at these keys.
            before = state_entries[before_idx]
            after = state_entries[after_idx]

            # Check if there is a valid diff at this range.
            # Diff is a change in state that is relevant for the segmentation, so it will crate a segment
            # Check only the states that are not shared between after and state entries ("-" of sets)
            diffs = self.filter_diffs(after.state_records - before.state_records, state_types)
            if diffs is not None:
                # If there is a diff, prepare to do sub-segmentation on the segment.
                sub_segment_states = set()
                if self.hierarchical:
                    for state_record in diffs:
                        corresponding_sub_states = ALLOWED_SUB_SEGMENTS_BY_STATE[state_record.state_type]
                        sub_segment_states.update(corresponding_sub_states)

                sub_segments = self._hierarchical_segments(
                    state_entries[before_idx : after_idx + 1], sub_segment_states
                )
                segments.append(
                    Segment(
                        before.frame_count,
                        after.frame_count - before.frame_count,
                        after.frame_count,
                        diffs,
                        sub_segments,
                    )
                )

                # Continue segmentation by moving the before_idx to start here.
                before_idx = after_idx

            # Increase the range of elements we're looking at by one.
            after_idx += 1

        return segments

    def get_segments(self):
        """
        Gets the segmentation as a list of segments
        :return: Single segment representing the entire demo, with subsegments for each of the found segments
        """
        segments = self._hierarchical_segments(self.state_history, self.state_types)
        if len(segments) > 0:
            return Segment(segments[0].start, segments[-1].end - segments[0].start, segments[-1].end, [], segments)
        else:
            # When there are no segments, e.g., when we do a roomlocation segmentation but the robot does not change of rooms
            return Segment(self.state_history[0].frame_count, 0, self.state_history[0].frame_count, [], [])

    def filter_diffs(self, state_records, state_types):
        """
        Filter the segments so that only objects in the given state directions are monitored.
        :param state_records: Record of organized states on the relevant state types for the segmentation
        :param state_types: Relevant state types to segment
        :return: The records from the input that
        """
        new_records = set()

        # Go through the records in the segment.
        for state_record in state_records:
            # Check if the state type is on our list
            if state_record.state_type not in state_types:
                continue

            logging.debug(
                "state_type: {}, objects: {}, value: {}".format(state_record[0], state_record[1], state_record[2])
            )

            # Check if any object in the record is on our list.

            # Mode is the type of state change direction we are interested in, e.g., inHandOfRobot from False to True
            mode = self.state_directions[state_record.state_type]
            accept = True
            if mode == SegmentationStateDirection.FALSE_TO_TRUE:
                accept = state_record.value
            elif mode == SegmentationStateDirection.TRUE_TO_FALSE:
                accept = not state_record.value

            # If an object in our list is part of the record, keep the record.
            if accept:
                new_records.add(state_record)

        # If we haven't kept any of this segment's records, drop the segment.
        if not new_records:
            return None

        return new_records

    def _serialize_segment(self, segment):
        """
        Serializes each segment of a segmentation
        The serialization includes the information of the segment such as start/end time, duration, state changes, and any subsegments
        :param segment: Segment to seriaze
        :return: Serialized segment in the form of a dictionary
        """
        stringified_entries = [
            {
                "name": state_record.state_type.__name__,
                "objects": [self.obj2str(obj) for obj in state_record.objects],
                "value": state_record.value,
            }
            for state_record in segment.state_records
        ]

        return {
            "start": segment.start,
            "end": segment.end,
            "duration": segment.duration,
            "state_records": stringified_entries,
            "sub_segments": [self._serialize_segment(sub_segment) for sub_segment in segment.sub_segments],
        }

    def _segment_to_dict_tree(self, segment, output_dict):
        stringified_entries = [
            (
                state_record.state_type.__name__,
                ", ".join(obj.category for obj in state_record.objects),
                state_record.value,
            )
            for state_record in segment.state_records
        ]

        entry_strs = ["%s(%r) = %r" % entry for entry in stringified_entries]
        key = "%d-%d: %s" % (segment.start, segment.end, ", ".join(entry_strs))
        sub_segments = {}
        for sub in segment.sub_segments:
            self._segment_to_dict_tree(sub, sub_segments)
        output_dict[key] = sub_segments

    def serialize_segments(self):
        # Make the root call to recursive function.
        return self._serialize_segment(self.get_segments())

    def __str__(self):
        out = ""
        out += "---------------------------------------------------\n"
        out += "Segmentation of %s\n" % self.object_selection.name
        out += "Considered states: %s\n" % ", ".join(x.__name__ for x in self.state_types)
        out += "---------------------------------------------------\n"
        output = {}
        self._segment_to_dict_tree(self.get_segments(), output)
        out += printree.ftree(output) + "\n"
        out += "---------------------------------------------------\n"
        return out


def parse_args(defaults=False):
    args_dict = dict()
    args_dict["demo_file"] = os.path.join(
        igibson.ig_dataset_path,
        "tests",
        "cleaning_windows_0_Rs_int_2021-05-23_23-11-46.hdf5",
    )
    args_dict["out_dir"] = os.path.join(os.path.dirname(inspect.getfile(behavior.examples)), "data")
    args_dict["replay_demo_file"] = os.path.splitext(args_dict["demo_file"])[0] + "_segm_replay.json"
    args_dict["profile"] = False
    args_dict["check_determinism"] = False
    if not defaults:
        parser = argparse.ArgumentParser(description="Run segmentation on an ATUS demo.")
        parser.add_argument(
            "--demo_file", type=str, help="Path (and filename) of demo to replay. If empty, test demo will be used."
        )
        parser.add_argument(
            "--out_dir", type=str, help="Directory to store results in. If empty, test directory will be used."
        )
        parser.add_argument(
            "--replay_demo_file", type=str, help="Path (and filename) of demo to save from the replay (for debugging)."
        )
        parser.add_argument(
            "--profile",
            action="store_true",
            help="Whether to profile the segmentation, outputting a profile HTML in the out path.",
        )
        parser.add_argument(
            "--check_determinism",
            action="store_true",
            help="Whether to check for determinism in the replay after segmenting.",
        )
        args = parser.parse_args()
        args_dict["demo_file"] = args.demo_file
        args_dict["out_dir"] = args.out_dir
        args_dict["replay_demo_file"] = args.replay_demo_file
        args_dict["profile"] = args.profile
        args_dict["check_determinism"] = args.check_determinism

    return args_dict


def get_default_segmentation_processors(profiler=None):
    """
    Create a set of callbacks to process demos when replaying and perform segmentation
    It returns two types of processors for segmentation: flat and per room (allows to see what room the agent is in)
    :param profiler: Profiler to measure performance when segmenting
    :return: A dictionary with two sets of segmentation processors: flat and per room
    """
    # This applies a "flat" segmentation (e.g. not hierarchical) using only the states supported by our simple action
    # primitives, i.e., can be caused by our action primitives
    flat_states = [
        object_states.Open,
        object_states.OnTop,
        object_states.Inside,
        object_states.InHandOfRobot,
        object_states.InReachOfRobot,
    ]  # States that can be achieved by the robot through action primitives
    flat_object_segmentation = DemoSegmentationProcessor(
        flat_states, SegmentationObjectSelection.TASK_RELEVANT_OBJECTS, label_by_instance=True, profiler=profiler
    )

    # This applies a hierarchical segmentation based on goal condition states. It's WIP and currently unused.
    goal_segmentation = DemoSegmentationProcessor(
        SegmentationStateSelection.GOAL_CONDITION_RELEVANT_STATES,
        SegmentationObjectSelection.TASK_RELEVANT_OBJECTS,
        hierarchical=True,
        label_by_instance=True,
        profiler=profiler,
    )

    # This applies a flat segmentation that allows us to see what room the agent is in during which frames.
    room_presence_segmentation = DemoSegmentationProcessor(
        ROOM_STATES, SegmentationObjectSelection.ROBOTS, diff_initial=True, profiler=profiler
    )

    return {
        # "goal": goal_segmentation,
        "flat": flat_object_segmentation,
        "room": room_presence_segmentation,
    }


def main(selection="user", headless=False, short_exec=False):
    """
    Segment a given demo into a sequence of predefined action primitives
    It assumes a predefined map of logic changes to action primitives that cause them
    """
    logging.getLogger().setLevel(logging.INFO)
    logging.info("*" * 80 + "\nDescription:" + main.__doc__ + "/n" + "*" * 80)

    defaults = selection == "random" and headless and short_exec
    args_dict = parse_args(defaults=defaults)

    # Create output directory if needed.
    if not os.path.exists(args_dict["out_dir"]):
        os.mkdirs(args_dict["out_dir"])

    # Set up the profiler
    profiler = None
    if args_dict["profile"]:
        profiler = pyinstrument.Profiler()

    # Create default segmentation processors.
    segmentation_processors = get_default_segmentation_processors(profiler)

    # Run the segmentations.
    logging.info("Run segmentation")
    if args_dict["check_determinism"]:
        demo_replaying_example.replay_demo_with_determinism_check(
            args_dict["demo_file"],
            replay_demo_file=args_dict["out_path"],
            start_callbacks=[sp.start_callback for sp in segmentation_processors.values()],
            step_callbacks=[sp.step_callback for sp in segmentation_processors.values()],
        )
    else:
        demo_replaying_example.replay_demo(
            args_dict["demo_file"],
            replay_demo_file=args_dict["replay_demo_file"],
            start_callbacks=[sp.start_callback for sp in segmentation_processors.values()],
            step_callbacks=[sp.step_callback for sp in segmentation_processors.values()],
        )

    logging.info("Save segmentation")
    demo_basename = os.path.splitext(os.path.basename(args_dict["demo_file"]))[0]
    for segmentation_name, segmentation_processor in segmentation_processors.items():
        json_file = "%s_%s_segm.json" % (demo_basename, segmentation_name)
        json_fullpath = os.path.join(args_dict["out_dir"], json_file)
        with open(json_fullpath, "w") as f:
            json.dump(segmentation_processor.serialize_segments(), f)

    # Print the segmentations.
    combined_output = ""
    for segmentation_processor in segmentation_processors.values():
        combined_output += str(segmentation_processor) + "\n"
    print(combined_output)

    # Save profiling information.
    if args_dict["profile"]:
        logging.info("Save profiling")
        html = profiler.output_html()
        html_file = demo_basename + "_segm_profile.html"
        html_path = os.path.join(args_dict["out_dir"], html_file)
        with open(html_path, "w") as f:
            f.write(html)


RUN_AS_TEST = True  # Change to True to run this example in test mode
if __name__ == "__main__":
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
