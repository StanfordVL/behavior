# Benchmark Setup

## Evaluating Generalization

The goal in BEHAVIOR is to help developing general, robust and versatile AI agents. 
However, generalization may have two interpretations:
- Versatility: the same solution is general enough to solve to multiple problems
- Extrapolation: the same solution is general enough to solve to problems not seen during development/training

When it comes to the household activities in BEHAVIOR, generalization can be measured along different dimensions, for example, different setups of the same activities, or different activities (what is usually studied in meta-learning and transfer learning).
In increasing order of difficulty, all these are possible levels of generalization of setups within the same activities:
- Generalizing to object poses
- Generalizing to object instances/classes
- Generalizing to furniture poses
- Generalizing to furniture instances/classes
- Generalizing to scene layouts

Our proposed setup to evaluate generalization (versatility and exploration) is the following: 
- Agents should be evaluated in the 100 activities. This avoids tailored solutions for a single activity.
- For each activity, the agent should be evaluated in **three different simulated houses**.
- For each simulated house, the agent should be evaluated in **three levels of generalization**:
    - Three activity instances (furniture pieces and arrangement, object models and arrangement) that have been used/seen during development/training.
    - Three activity instances where the furniture and object models are the same as during development/training, but the arrangement of the objects is new.
    - Three activity instances where the furniture is new.
    
## Alternative Benchmark Setups

The ultimate setup in BEHAVIOR is to perform the 100 activities in their full complexity as they should be solved in the real-world: using only onboard sensing, planning the best strategies to achieve the long horizon goals, and controlling the execution of these strategies through motion of the robot at each step that produces the right effect in the physical simulated world.
However, we acknowledge the extreme complexity of this setup.
Therefore, we propose a set of alternative setups to study different aspects of the BEHAVIOR activities with more emphasis in perception, planning or control.

#### Original Setup

- Observations: Onboard sensor signals
- Actuation: Control commands at 30 Hz

#### Changing Observations

The setup could be simplified to an easier perceptual challenge by changing the observations available to the agent. 
Alternatives for the observations include:
- Localization of the agent in the scene.
- List of objects in the environment.
- Full scene graph of the environment. The scene graph includes all objects, their properties, and the relationships to other objects.
- Full observability: The observations include any information that can be queried from the simulator, e.g., full object models, their state, ...

#### Changing Actuation

The setup could be simplified to an easier control challenge by changing the actuation available to the agent. 
Alternatives for the actuation include:
- Predefined set of parameterized action primitives. The agent selects one primitive and its parameters, and the primitive executes for a extended period of time.
We provide an initial set of primitives with semantic outcomes (`pick`, `place`, `open`, `close`, `navigate to`).
Critical for the performance of the agents here is the available set of primitives and their implementation.


