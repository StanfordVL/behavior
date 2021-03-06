class Agent(object):
    """
    Abstract class that an agent should implement to be used in our benchmarking pipeline
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def reset(self):
        """
        Reset function
        To be called every time that the environment resets
        Usually clears the state and motion
        """
        pass

    def act(self, obs):
        """
        Main function of the agent
        Given an observation, the agent needs to provide an action
        :param obs: observation from the environment to decide the next action
        :returns: action taken by the agent given the observation (and any internal information)
        """
        pass
