import collections
import os

import numpy as np
import torch
from IPython import embed
from stable_baselines3 import PPO

IMG_WIDTH = 128
IMG_HEIGHT = 128
PROPRIOCEPTION_DIM = 20


class PPOAgent(object):
    def __init__(self, ckpt_path="checkpoints/onboard_sensing_ppo_random"):
        self.agent = PPO.load(ckpt_path)

    def reset(self):
        pass

    def act(self, obs):
        return self.agent.predict(obs, deterministic=True)[0]


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
