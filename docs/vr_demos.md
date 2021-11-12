# The BEHAVIOR Dataset of Human Demonstrations in Virtual Reality

The BEHAVIOR dataset includes 500 demonstrations of human participants performing BEHAVIOR-100 activities in iGibson 2.0 using a virtual reality interface. The data was collected by 5 participants using an HTC Vive Pro Eye headset with 2 HTC Vive Wand controllers and 1 torso tracker strapped to the participant’s waist. The participants were cued by a VR overlay describing activity goal conditions. Activity relevant objects corresponding to a goal condition were highlighted on the user view on-demand, guiding human execution. The text of the corresponding part of the condition switched from red to green at the completion of a given part.

There are two available HDF5 datasets. The first is processed for imitation learning, containing rendered sensor modalities matching the observation of the agent, as well as the recorded action. The second is the “raw” unprocessed observations which include additional data from the VR recordings and simulator state of the activity-relevant objects.

Note: Since every small change in the simulator may cause deviating changes in execution, if you want to replay the demos (run the actions stored in the demonstration file, and reproduce the exact same outcomes, e.g. states/images), this comes with some caveats. You must:
1) Be on Windows
2) Use the `pybullet-svl` fork (`pip install pybullet-svl`, as in setup.py of iGibson)
3) Use the `behavior-replay` branch of iGibson
4) Download the behavior-replay version of BEHAVIOR dataset bundle (BEHAVIOR Dataset of Objects and iGibson Dataset) via [this link](https://forms.gle/GXAacjpnotKkM2An7 )

Following the instructions above, we have verified that the 500 demos can be replayed and reproduced perfectly.

## BEHAVIOR HDF5 Specification (Processed Dataset)

The following are the available keys to index into the hdf5 file. The dimensionality of each component is noted parenthetically, where `N` indicates the number of frames in the demo.

- action (N x 28) -- see BehaviorRobot description in the [Embodiments section](agents.md) for details about the actuation of this robot. This vector contains two additional dimensions that correspond to the `hand reset` action in VR: an action that teleports the simulated hands to the exact pose of the VR hand controller when they have diverged. This actions are not used by AI agents but are necessary to understand the demos.
- proprioception (N x 20) -- proprioceptive feedback
- rgb (N x 128 x 128 x 3) -- rgb image from camera
- depth (N x 128 x 128 x 1) -- depth map
- seg (N x 128 x 128 x 1) -- segmentation of scene
- ins_seg (N x 128 x 128 x 1) -- instance segmentation
- highlight ( N x 128 x 128 x 1) -- activity relevant object binary mask, active for all objects included in the activity goal (except the agent and the floor)
- task_obs (N x 456) -- task observations, including ground truth state of the robot, and ground truth poses and grasping state of a maximum of a fixed number of activity relevant objects

