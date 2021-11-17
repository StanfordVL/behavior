# The BEHAVIOR Dataset of Human Demonstrations in Virtual Reality

The BEHAVIOR dataset includes 500 demonstrations of human participants performing BEHAVIOR-100 activities in iGibson 2.0 using a virtual reality interface. The data was collected by 5 participants using an HTC Vive Pro Eye headset with 2 HTC Vive Wand controllers and 1 torso tracker strapped to the participant’s waist. The participants were cued by a VR overlay describing activity goal conditions. Activity relevant objects corresponding to a goal condition were highlighted on the user view on-demand, guiding human execution. The text of the corresponding part of the condition switched from red to green at the completion of a given part.

There are two available HDF5 datasets. The first is processed for imitation learning, containing rendered sensor modalities matching the observation of the agent, as well as the recorded action. The second is the “raw” unprocessed observations which include additional data from the VR recordings and simulator state of the activity-relevant objects.

Note: Since every small change in the simulator may cause deviating changes in execution, if you want to replay the demos (run the actions stored in the demonstration file, and reproduce the exact same outcomes, e.g. states/images), this comes with some caveats. You must:
1) Be on Windows
2) Use the `pybullet-svl` fork (`pip install pybullet-svl`, as in setup.py of iGibson)
3) Use the `behavior-replay` branch of iGibson
4) Download the behavior-replay version of BEHAVIOR dataset bundle (BEHAVIOR Dataset of Objects and iGibson Dataset) via [this link](https://forms.gle/GXAacjpnotKkM2An7 )

Following the instructions above, we have verified that the 500 demos can be replayed and reproduced perfectly.

## BEHAVIOR HDF5 Processed Dataset

We provide a processed dataset generated from the raw files and that includes images and proprioceptive sensing.
Alternative processed datasets can be generated based on the raw files, e.g. with different image resolutions.

### HDF5 Content
The following are the available keys to index into the hdf5 file. The dimensionality of each component is noted parenthetically, where `N` indicates the number of frames in the demo.

- action (N x 28) -- see BehaviorRobot description in the [Embodiments section](agents.md) for details about the actuation of this robot. This vector contains two additional dimensions that correspond to the `hand reset` action in VR: an action that teleports the simulated hands to the exact pose of the VR hand controller when they have diverged. These actions are not used by AI agents but are necessary to understand the demos.
- proprioception (N x 22) -- proprioceptive feedback. More details in the [Embodiments section](agents.md).
- rgb (N x 128 x 128 x 3) -- rgb image from camera
- depth (N x 128 x 128 x 1) -- depth map
- seg (N x 128 x 128 x 1) -- segmentation of scene
- ins_seg (N x 128 x 128 x 1) -- instance segmentation
- highlight ( N x 128 x 128 x 1) -- activity relevant object binary mask, active for all objects included in the activity goal (except the agent and the floor)
- task_obs (N x 456) -- task observations, including ground truth state of the robot, and ground truth poses and grasping state of a maximum of a fixed number of activity relevant objects

## BEHAVIOR HDF5 Raw Dataset

### Accessing the BEHAVIOR hdf5 demo files
This code snipped provides access to the data using the python's hdf5 module that is dependency of iGibson:
```
import h5py
import numpy

frame_number = 0
hf = h5py.File(‘/path/to/behavior/demo.hdf5’)

# see below for metadata description
activity_name = hf.attrs[‘metadata/task_name’]
print(activity_name)

# see below for finding indices for array
position_of_hmd = np.array(hf[‘frame_data’][‘vr_device_data’][‘hmd’][frame_number, 1:4])

```

### Metadata
The metadata can be accessed by keying into the hdf5.attrs with the following keys:
- `/metadata/start_time`: the date the demo was recorded
- `/metadata/physics_timestep`: the simulated time duration of each step of the physics simulator (1/300 seconds for all our demos)
- `/metadata/render_timestep`: the simulated time between each rendered image, determines the framerate (1/30 seconds). `render_timestep / physics_timestep` gives the number of physics simulation steps between two generated images (10)
- `/metadata/git_info`: the git info for activity definition, `iGibson`, `ig_dataset`, and `ig_assets`. This is used to ensure participants are using a compatible version of iGibson if replaying the demo
- `/metadata/task_name`: The name of the activity, e.g. `washing_dishes`, `putting_away_groceries`...
- `/metadata/task_instance`: The instance of the activity that specifies the state (pose, extended state) of the sampled activity relevant objects at initialization
- `/metadata/scene_id`: The scene (`Rs_int`, `Wainscott_0_int`, etc.) where the activity was recorded
- `/metadata/filter_objects`: Whether only activity relevant objects were recorded in the activity
- `/metadata/obj_body_id_to_name`: mapping of pybullet IDs to the semantic object name


### HDF5 Content

The following are the available keys to index into the hdf5 file. The dimensionality of each component is noted parenthetically, where `N` indicates the number of frames in the demo.

- `frame_data` (N x 4) 
    - `goal_status` 
        - `satisfied` (N x total_goals) -- Total satisfied top-level predicates, where total_goals is the number of predicates 
        - `unsatisfied` (N x total_goals) -- Total unsatisfied top-level predicates, where total_goals is the number of predicates 
- `physics_data` 
    - `string` (bullet_id: total number of activity-relevant scene objects)
    - `position` (N x 3) -- The 3D position of the object center of mass
    - `orientation` (N x 4) -- The quaternion orientation of the object
    - `joint_state` (N x number of object joints) -- The pybullet joint state of each object 
- `vr` 
    - `vr_camera`
        - `right_eye_view` (N x 4 x 4) -- the view projection matrix
        - `right_eye_proj` (N x 4 x 4) -- the camera projection matrix 
        - `right_camera_pos` (N x 3) -- The 3D position of the camera 
    - `vr_device_data` 
        - `hmd` (N x 17) -- see below
        - `left_controller` (N x 27) -- see below
        - `right_controller` (N x 27) -- see below 
        - `vr_position_data` (N x 12) -- see below
        - `torso_tracker` (N x 8) -- see below
    - `vr_button_data`
        - `left_controller` (N x 3) -- see below
        - `right_controller` (N x 3) -- see below
    - `vr_eye_tracking_data` 
        - `left_controller` (N x 9) -- see below 
    - `vr_event_data` 
        - `left_controller` (N x 28) -- see below
        - `right_controller` (N x 28) -- see below
        - `reset_actions` (N x 2) -- reset for left and right controller
- `Agent_actions`
    - `vr_robot` (N x 28) -- see BEHAVIOR robot description in previous section
- `action` -- unused 

Additional description of the dimensions of the arrays noted above: the following are not keys but correspond to indices of the associated array:

- `hmd` (17) 
    - hmd tracking data is valid (1)
    - translation (3) 
    - rotation (4)
    - right vector (3) 
    - up vector (3)
    - forward vector (3)
- `left_controller`/`right_controller` (27) 
    - controller tracking data is valid (1)
    - translation (3)
    - rotation (4)
    - right vector (3) 
    - up vector (3)
    - forward vector (3)
    - base_rotation (4)
    - base_rotation * controller_rotation (4)
    - applied_force (6) -- p.getConstraintState(controller_constraint_id)
- `vr_button_data`
    - trigger fraction (1) --- open: 0 -> closed: 1 
    - touchpad x position (1) -- left: -1 -> right: 1
    - touchpad y position (1) -- bottom: -1 -> right: 1
- `Vr_eye_tracking_data`
    - eye-tracking data is valid (1)
    - origin of gaze in world space (3) 
    - direction vector of gaze in world space (3)
    - left pupil diameter (1)
    - right pupil diameter (1) 
- `vr_position_data` (12)
    - position of the system in iGibson space (3)
    - offset of the system from the origin (3)
    - applied force to vr body (6) -- p.getConstraintState(body_constraint_id)
- `torso_tracker` (8)
    - torso tracker is valid (1)
    - position (3)
    - rotation (4) 

## Add your own demos!

Coming soon!
