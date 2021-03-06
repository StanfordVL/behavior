import numpy as np
from stable_baselines3 import PPO

from behavior.benchmark.agents.agent import Agent

IMG_WIDTH = 128
IMG_HEIGHT = 128
PROPRIOCEPTION_DIM = 20


class PPOAgent(Agent):
    """
    Implementation of the Agent class that loads a checkpoint of a previously trained PPO policy and queries the policy
    with the received observations to obtain actions
    """

    def __init__(self, ckpt_path="checkpoints/onboard_sensing_ppo_random"):
        self.agent = PPO.load(ckpt_path)

    def reset(self):
        pass

    def act(self, obs):
        return self.agent.predict(obs, deterministic=True)[0]


# Test to print actions
if __name__ == "__main__":
    obs = {
        "rgb": np.ones((IMG_HEIGHT, IMG_WIDTH, 3)),
        "depth": np.ones((IMG_HEIGHT, IMG_WIDTH, 1)),
        "seg": np.ones((IMG_HEIGHT, IMG_WIDTH, 1)),
        "ins_seg": np.ones((IMG_HEIGHT, IMG_WIDTH, 1)),
        "highlight": np.ones((IMG_HEIGHT, IMG_WIDTH, 1)),
        "proprioception": np.ones((PROPRIOCEPTION_DIM,)),
    }
    agent = PPOAgent(ckpt_path="checkpoints/onboard_sensing_ppo_random")
    action = agent.act(obs)
    print("action", action)
