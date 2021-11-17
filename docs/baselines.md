# Baselines

We provide a set of common baselines from the Robot Learning literature to help create and develop new solutions for BEHAVIOR.
Our baselines include imitation learning and reinforcement learning, both in the original low-level action space of the benchmark, and making use of our provided set of action primitives based on sampling-based motion planning.
Here, we briefly describe the baselines you can find in this repository.

#### Imitation Learning Baseline
A simple behavioral cloning (BC) baseline can be found [here](https://github.com/StanfordVL/behavior-baselines/tree/main/behavior_baselines/behavioral_cloning).
Please note that you need to download our [imitation learning dataset](https://behavior.stanford.edu/vr-demos) first. 

There are two BC agents in (`simple_bc_agent.py`):

1)(`BCNet_rgbp`): A BC agent that uses an RGB image (128x128) and proprioception feedback (20) as state space. 

2)(`BCNet_taskObs`): A BC agent that uses task observations (456) and proprioception feedback (20) as state space. 

Details about state information can be found [here](https://stanfordvl.github.io/behavior/vr_demos.html). Feel free to include additional state information such as depth, instance segmentation, etc.

Both agents are based on the BehaviorRobot, you can find more details about its action space [here](https://stanfordvl.github.io/behavior/agents.html#behaviorrobot). Please note that the action vector in human VR demo contains two additional dimensions that correspond to the hand reset action in VR: an action that teleports the simulated hands to the exact pose of the VR hand controller when they have diverged. These actions are not used by the agents but are necessary to understand the demos. 

#### Reinforcement Learning Baseline in the Original Action Space

#### Reinforcement Learning Baseline with Action Primitives
