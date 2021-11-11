import argparse

from igibson.challenge.behavior_challenge import BehaviorChallenge

from rl_agent import PPOAgent
from simple_agent import RandomAgent


def get_agent(agent_class, ckpt_path=""):
    if agent_class == "Random":
        return RandomAgent()
    elif agent_class == "PPO":
        return PPOAgent(ckpt_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-class", type=str, default="Random", choices=["Random", "PPO"])
    parser.add_argument("--ckpt-path", default="", type=str)

    args = parser.parse_args()

    agent = get_agent(agent_class=args.agent_class, ckpt_path=args.ckpt_path)
    challenge = BehaviorChallenge()
    challenge.submit(agent)


if __name__ == "__main__":
    main()
