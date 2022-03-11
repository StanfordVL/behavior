import numpy as np

from behavior.benchmark.agents.agent import Agent

ACTION_DIM = 26
IMG_WIDTH = 128
IMG_HEIGHT = 128
PROPRIOCEPTION_DIM = 20


class RandomAgent(Agent):
    """
    Implementation of the Agent class that generates random actions given an observation
    """

    def __init__(self):
        pass

    def reset(self):
        pass

    def act(self, obs):
        action = np.random.uniform(low=-1, high=1, size=(ACTION_DIM,))
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
