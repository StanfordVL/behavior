# Training Agents

Any type of robotic agent can be evaluated on the BEHAVIOR benchmark. However, in recent years, machine learning based agents have gained popularity for robotics and embodied AI tasks. We provide scripts and functionalities to help training policies for agents.

### Training after a manual installation

The training procedure will strongly depend on your type of solution/policy.
However, we provide an example of parallel training code with `Stable Baselines 3` that may help you get started with your own solution. You can run our example by executing:
```
python -m behavior.examples.training_example
```
Please, be aware that this code won't converge to a fully successful solution for BEHAVIOR ;).


### Training after a Docker installation

To train on a `minival` split (on a single activity) use the following script: 
```
./benchmark/scripts/train_minival_locally.sh --docker-name my_submission --dataset-path my/path/to/dataset
```
where `my_submission` is the name of the docker image, and `my/path/to/dataset` corresponds to the path to the BEHAVIOR bundle (3D objects and scenes dataset) and the `igibson.key` from the [installation instructions](installation.md).

Note that due to the complexity of all BEHAVIOR activities, the provided parallel training with PPO from Stable Baselines 3 is NOT expected to converge. We provide this training pipeline just as a starting point for users to start their own training.

Modify the script to change the activity or activities the agent is trained on, and other parameters.