#  The BEHAVIOR Benchmark

![mosaicgif.gif](images/mosaicgif.gif)
##### Benchmark for Everyday Household Activities in Virtual, Interactive, and Ecological Environments

BEHAVIOR is a benchmark for embodied AI agents to complete 100 household activities in simulation.
In BEHAVIOR, the AI agents need to control a robot's embodiment taking decisions based on acquired virtual sensor signals, and executing them with control action commands.
The complexity, realism and diversity of the benchmark creates a complex challenge for modern AI solutions.

In this documentation, you will find information to use BEHAVIOR to train, develop and evaluate your solutions.
You will have to install and use iGibson, our open source simulation environment, and the BEHAVIOR Dataset of Objects (more in the [installation instructions](installation.md)).
You will also find details about the benchmark setup such as the [embodiments available](agents.md), the control and sensing alternatives, the metrics, and the [activities](activities.md).
This documentation includes also useful information to get started with examples.

We hope to make BEHAVIOR a useful evaluation tool in AI and robotics. Please, [contact us](mailto:behavior.benchmark@gmail.com) if you have any questions or suggestions.


### Citation
If you use BEHAVIOR, its assets and models, consider citing the following publications:

```
@inproceedings{shen2021igibson,
      title={BEHAVIOR: Benchmark for Everyday Household Activities in Virtual, Interactive, and Ecological Environments}, 
      author={Sanjana Srivastava and Chengshu Li and Michael Lingelbach and Roberto Mart\'in-Mart\'in and Fei Xia and Kent Vainio and Zheng Lian and Cem Gokmen and Shyamal Buch and Karen Liu and Silvio Savarese and Hyowon Gweon and Jiajun Wu and Li Fei-Fei},
      booktitle={Conference in Robot Learning (CoRL)},
      year={2021},
      pages={accepted}
}
```

```
@inproceedings{li2021igibson,
      title={iGibson 2.0: Object-Centric Simulation for Robot Learning of Everyday Household Tasks}, 
      author={Chengshu Li and Fei Xia and Roberto Martín-Martín and Michael Lingelbach and Sanjana Srivastava and Bokui Shen and Kent Vainio and Cem Gokmen and Gokul Dharan and Tanish Jain and Andrey Kurenkov and Karen Liu and Hyowon Gweon and Jiajun Wu and Li Fei-Fei and Silvio Savarese},
      booktitle={Conference in Robot Learning (CoRL)},
      year={2021},
      pages={accepted}
}
```

### Repositories
There are three main repositories necessary to evaluate with BEHAVIOR:
- The `behavior` repository (https://github.com/StanfordVL/behavior) with the code to evaluate and useful baselines to get started.
- The `igibson` repository (https://github.com/StanfordVL/iGibson) with the code of our simulator.
- The `bddl` repository (https://github.com/StanfordVL/bddl) with the library for the logic language BDDL used to define activities.

Additionally, you will need to obtain access and download the BEHAVIOR Dataset of Objects, with 3D annotated object models for the evaluation, and the iGibson dataset and assets with house scenes and robot models.

### Documentation
General information about our benchmark can be found in our webpage: http://behavior.stanford.edu or in our publication available [on arxiv](https://arxiv.org/abs/2108.03332).

For specific documentation about the iGibson simulator, please visit http://svl.stanford.edu/igibson/docs or refer to our publications, the [iGibson 2.0 arxiv preprint](https://arxiv.org/abs/2108.03272) and the [iGibson 1.0 arxiv preprint](https://arxiv.org/abs/2012.02924).

More information about BDDL can be found at https://github.com/StanfordVL/bddl and in our [BEHAVIOR publication](https://arxiv.org/abs/2108.03332).