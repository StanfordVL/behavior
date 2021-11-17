# Training and Evaluating Agents

Once you have installed BEHAVIOR and its dependencies, you can start training and evaluating agents.
The way to do it will depend on your type of installation: manual or Docker installation.
In the following, we include instructions for training and evaluation for both installation types.

### Training and Benchmarking after a Manual Installation

#### Training 

The training procedure will strongly depend on your type of solution.
However, we provide an example of parallel training code with `Stable Baselines 3` that may help you derive your own.
You can run our example by executing:
```
python -m igibson.examples.demo.stable_baselines3_behavior_example
```
Please, be aware that this code won't converge to a solution ;).

#### Evaluating and Benchmarking

You can evaluate locally using the code in this repository (`behavior_benchmark.py`). 
As an example, the following code evaluates a random agent on a single activity specified in an environment config file:
```
python behavior/benchmark/behavior_benchmark.py
```
The code evaluates the agent following the official [benchmarking setup](setups.md) of nine instances of the activity with increasing complexity: three instances of the activity that are expected to be the same as in training, three instances where everything is the same as in training but the small objects change their initial locations, and three instances where the furniture in the scenes is also different.
The code also runs the evaluation metrics and saves the values on files.

To evaluate your agent, you can modify the main function in `behavior_benchmark.py`, or directly use the `BehaviorBenchmark` object in your code and specify the agent to evaluate, and the activities, scene and instances to be evaluated in.
Your agent should implement the functions `reset()` and `act(observations)`, ideally inheriting from the class `Agent` in `agent.py`.
See more examples [here](examples.md).

### Training and Benchmarking in a Docker Installation

#### Training

To train on a `minival` split (on a single activity) use the following script: 
```
./benchmark/scripts/train_minival_locally.sh --docker-name my_submission --dataset-path my/path/to/dataset
```

Note that due to the complexity of all BEHAVIOR activities, the provided parallel training with PPO from Stable Baselines 3 is NOT expected to converge. 
We provide this training pipeline just as a starting point for participants to further build upon.


#### Evaluating

You can evaluate locally for the `minival` split (one single activity) executing:
```
./benchmark/scripts/test_minival_locally.sh --docker-name my_submission
```

You can also evaluate locally for the `dev` split (all activities) executing:

```
./benchmark/scripts/test_dev_locally.sh --docker-name my_submission --dataset-path my/path/to/dataset
```

#### Online Submission to the Public Leaderboard on EvalAI

If you use the Docker installation, you can submit your solution to be evaluated and included in the public leaderboard.
For that, you first need to register for our benchmark on EvalAI [here](https://eval.ai/web/challenges/challenge-page/1190/overview).
You should follow the instructions in the `submit` tab on EvalAI that we summarize here:
```
# Installing EvalAI Command Line Interface
pip install "evalai>=1.2.3"

# Set EvalAI account token
evalai set_token <your EvalAI participant token>

# Push docker image to EvalAI docker registry
evalai push my_submission:latest --phase <track-name>
```

There are two valid benchmark tracks depending if your agent uses only onboard sensing or assumes full observabilty: `behavior-test-onboard-sensing-1190`, `behavior-test-full-observability-1190`.
Once we receive your submission, we evaluate and return the results. 
Due to the time and resource consuming evaluation process, each participant is restricted to submit once per week, maximum 4 times per month.