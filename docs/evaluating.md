# Training and Evaluating Agents

Once you have installed BEHAVIOR and its dependencies, you are ready to evaluate your agents on the benchmark. To be evaluated, agents have to be instantiated as objects of the class `Agent` or derived. We have created an initial derived class `CustomAgent` in `behavior/benchmark/agents/users_agent.py` to be fulfilled for your agent. The minimal functionality necessary for your agent is a `reset` function and the `act` action that provides actions at each timestep, given an observation from the environment. 

Once your agent is implemented as derived from the `Agent` class, you can evaluate it in BEHAVIOR activities. The way to do it will depend on your type of installation: manual or Docker installation. In the following, we include instructions for evaluation for both installation types.

### Evaluating an agent on BEHAVIOR after a manual installation

To evaluate locally, use the functionalities in `behavior/benchmark/behavior_benchmark.py`. As an example, the following code benchmarks a random agent on a single activity indicated in the specified environment config file:
```
export CONFIG_FILE=path/to/your/config/for/example/behavior/configs/behavior_onboard_sensing.yaml
export OUTPUT_DIR=path/to/your/output/dir/for/example/tmp
python -m behavior.benchmark.behavior_benchmark
```
Once you have implemented your agent in the class `CustomAgent`, you can evaluate it instead of the random agent by changing the last command by:
```
python -m behavior.benchmark.behavior_benchmark --agent-class Custom
```

The code in `behavior_benchmark.py` can be used to evaluate an agent following the official [setup](setups.md) benchmark rules: the agent is evaluated in the indicated activity/activities for nine instances of increasing complexity: three instances of the activity that were available for training, three instances where everything is the same as in training but the small objects change the objects initial locations, and three instances where the furniture in the scenes is also different. The code runs the benchmark metrics and saves the values on files in the `OUTPUT_DIR`.

The example above evaluates the random agent in a single activity specified in the environment's config file. However, you can select the activity you want to benchmark the agent on with the option `--split` and the name of the activity (check all activities [here](https://behavior.stanford.edu/activity_list.html) and video examples [here](https://behavior.stanford.edu/behavior-gallery/activity.html)), or benchmark on the entire set of 100 activities by specifying `--split dev` or `--split test`, to use developing or test activity instances. 

For example, to benchmark a provided PPO agent (reinforcement learning) loading a specific policy checkpoint only for the activity `cleaning_toilet`, you can execute:
```
export CONFIG_FILE=path/to/your/config/for/example/behavior/configs/behavior_onboard_sensing.yaml
export OUTPUT_DIR=path/to/your/output/dir/for/example/tmp
python -m behavior.benchmark.behavior_benchmark --agent-class PPO --ckpt-path /tmp/my_checkpoint --split cleaning_toilet
```
We provide pretrained checkpoints in `behavior/benchmark/agents/checkpoints`


#### Evaluating on a single instance

Instead of evaluating agents following the benchmark rules (nine instances per activity), you can also evaluate in one or a custom set of activity instances by calling directly the method `BehaviorBenchmark.evaluate_agent_on_one_activity` and providing a list of instances.

### Evaluating an agent on BEHAVIOR after a Docker installation

We provide several scripts to evaluate agents on `minival` and `dev` splits. The `minival` split serves to evaluate on a single activity. The following code evaluates a random agent on the `minival` split using a local docker image:
```
./benchmark/scripts/test_minival_docker.sh --docker-name my_submission --dataset-path my/path/to/dataset
```
where `my_submission` is the name of the docker image, and `my/path/to/dataset` corresponds to the path to the iGibson and BEHAVIOR Datasets, and the `igibson.key` obtained following the [installation instructions](installation.md).

You can also evaluate locally for the `dev` split (all activities) by executing:
```
./benchmark/scripts/test_dev_docker.sh --docker-name my_submission --dataset-path my/path/to/dataset
```

Both scripts call `behavior/benchmark/scripts/evaluate_agent.sh`. You can modify this script, or the docker scripts to evaluate your agent.

#### Submitting to the BEHAVIOR public leaderboard on EvalAI

If you use the Docker installation, you can submit your solution to be evaluated and included in the public leaderboard. For that, you first need to register for our benchmark on EvalAI [here](https://eval.ai/web/challenges/challenge-page/1190/overview). You should follow the instructions in the `submit` tab on EvalAI that we summarize here:
```
# Installing EvalAI Command Line Interface
pip install "evalai>=1.2.3"

# Set EvalAI account token
evalai set_token <your EvalAI participant token>

# Push docker image to EvalAI docker registry
evalai push my_submission:latest --phase <track-name>
```

There are two valid benchmark tracks depending if your agent uses only onboard sensing or assumes full observability: `behavior-test-onboard-sensing-1190`, `behavior-test-full-observability-1190`.
Once we receive your submission, we evaluate and return the results. 
Due to the time and resource consuming evaluation process, each participant is restricted to submit once per week, maximum 4 times per month.