from behavior.benchmark.agents.agent import Agent


class CustomAgent(Agent):
    """
    Entry point for BEHAVIOR users
    """

    def __init__(self):
        """
        Constructor
        """
        raise NotImplementedError

    def reset(self):
        """
        Reset function
        To be called every time that the environment resets
        Usually clears the state and motion
        """
        raise NotImplementedError

    def act(self, obs):
        """
        Main function of the agent
        Given an observation, the agent needs to provide an action
        :param obs: observation from the environment to decide the next action
        :returns: action taken by the agent given the observation (and any internal information)
        """
        raise NotImplementedError
