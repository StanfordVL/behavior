import numpy as np
from igibson.robots import REGISTERED_ROBOTS

from behavior.benchmark.agents.agent import Agent

IMG_WIDTH = 128
IMG_HEIGHT = 128
PROPRIOCEPTION_DIM = 20


class RandomAgent(Agent):
    """
    Implementation of the Agent class that generates random actions given an observation
    """

    def __init__(self, robot_type="BehaviorRobot"):
        # TODO: It would be better to query directly the action space dim but that requires loading all robots. We
        # hardcode them. This may fail if the robot uses an unexpected controller type
        assert robot_type in REGISTERED_ROBOTS.keys(), "The given robot_type ({}) does not exist in iGibson".format(
            robot_type
        )
        if robot_type == "BehaviorRobot":
            self.action_dim = 28  # Maybe less work too
        elif robot_type == "Husky":
            self.action_dim = 4
        elif robot_type == "Locobot":
            self.action_dim = 2
        elif robot_type == "Turtlebot":
            self.action_dim = 2
        elif robot_type == "Fetch":
            self.action_dim = 11
        elif robot_type == "Freight":
            self.action_dim = 2
        elif robot_type == "JR2":
            self.action_dim = 8
        elif robot_type == "Ant":
            self.action_dim = 8
        pass

    def reset(self):
        pass

    def act(self, obs):
        action = np.random.uniform(low=-1, high=1, size=(self.action_dim,))
        return action


# Test to print random actions
if __name__ == "__main__":
    obs = {
        "rgb": np.ones((IMG_HEIGHT, IMG_WIDTH, 3)),
        "depth": np.ones((IMG_HEIGHT, IMG_WIDTH, 1)),
        "seg": np.ones((IMG_HEIGHT, IMG_WIDTH, 1)),
        "ins_seg": np.ones((IMG_HEIGHT, IMG_WIDTH, 1)),
        "highlight": np.ones((IMG_HEIGHT, IMG_WIDTH, 1)),
        "proprioception": np.ones((PROPRIOCEPTION_DIM,)),
    }
    agent = RandomAgent()
    action = agent.act(obs)
    print("action", action)
