# The BEHAVIOR Dataset of Activity Definitions and BDDL

Each BEHAVIOR activity is defined as a categorized object list, an initial condition, and a goal condition using the BEHAVIOR Domain Definition Language, a language to define logic-symbolic statements. 
Although BDDL shares some of the syntax and characteristics of the Planning Domain Definition Language (PDDL), e.g., both represent first-order logic, they are different as BDDL does not include action symbols and cannot be used for symbolic planning. 

In BDDL, the initial condition is a set of logical statements that are true for any valid initial state. 
The statements specify positional relationships between pairs of objects (e.g., `insideOf(Apple, Fridge)`) and non-kinematic states of individual objects (e.g. `cooked`, `toggledOn`, `notDusty`). 
The goal condition is a logical expression that specifies the objective of the activity. 
Since the same logic condition may correspond to multiple simulator states (e.g., multiple poses of objects `o1` and `o2` correspond to `insideOf(o1, o2)`), BDDL covers a large variety of ways to achieve each activity.

iGibson 2.0 implements functionalities to read this initial state and sample concrete simulation states (e.g., object poses, temperature, toggling state) that correspond to the logic statements. 
We provide a set of these concrete simulator initial states that we call activity instances or caches. 
We provide a set of instances for training, but you can generate their own instances as well (see how to [generate your own activity](##Add your own activity!)). 

For each activity instance, the simulator is instantiated following the concrete specified state, the embodied AI agents perform the activity, and the simulator iGibson 2.0 checks at each step if the logic expression in the goal condition has been fulfilled. 
The episode ends when the expression is fulfilled or the time is up. 

## Add your own activity!

Coming soon!
