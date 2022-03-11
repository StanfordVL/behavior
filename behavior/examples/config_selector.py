import logging
import os
from sys import platform

import igibson
import yaml
from igibson.envs.igibson_env import iGibsonEnv
from igibson.render.profiler import Profiler
from igibson.utils.assets_utils import folder_is_hidden
from igibson.utils.utils import let_user_pick

import behavior


def main(selection="user", headless=False, short_exec=False):
    """
    Prompts the user to select any available interactive scene and loads a turtlebot into it.
    It steps the environment 100 times with random actions sampled from the action space,
    using the Gym interface, resetting it 10 times.
    """

    print("*" * 80 + "\nDescription:" + main.__doc__ + "\n" + "*" * 80)

    available_configs = get_first_options()
    config_id = available_configs[let_user_pick(available_configs, selection=selection) - 1]
    print("Using config file " + config_id)
    config_filename = os.path.join(behavior.configs_path, config_id)
    config_data = yaml.load(open(config_filename, "r"), Loader=yaml.FullLoader)
    # Reduce texture scale for Mac.
    if platform == "darwin":
        config_data["texture_scale"] = 0.5
    config_data["image_width"] = 512
    config_data["image_height"] = 512
    config_data["vertical_fov"] = 60
    # config_data["load_object_categories"] = []  # Uncomment this line to accelerate loading with only the building
    env = iGibsonEnv(config_file=config_data, mode="gui_interactive" if not headless else "headless")
    max_iterations = 10 if not short_exec else 1
    for j in range(max_iterations):
        print("Resetting environment")
        env.reset()
        for i in range(100):
            with Profiler("Environment action step"):
                action = env.action_space.sample() * 0.05
                state, reward, done, info = env.step(action)
                if done:
                    print("Episode finished after {} timesteps".format(i + 1))
                    break
    env.close()


def get_first_options():
    config_path = behavior.configs_path
    available_configs = sorted(
        [
            f
            for f in os.listdir(config_path)
            if (not folder_is_hidden(f) and os.path.isfile(os.path.join(config_path, f)))
        ]
    )
    return available_configs


RUN_AS_TEST = False  # Change to True to run this example in test mode
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if RUN_AS_TEST:
        main(selection="random", headless=True, short_exec=True)
    else:
        main()
