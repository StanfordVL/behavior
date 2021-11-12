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

### Code Release
The GitHub repository of iGibson can be found [here](https://github.com/StanfordVL/iGibson). Bug reports, suggestions for improvement, as well as community developments are encouraged and appreciated. 

### Documentation
The documentation for iGibson can be found [here](http://svl.stanford.edu/igibson/docs/). It includes installation guide (including data download instructions), quickstart guide, code examples, and APIs.

If you want to know more about iGibson, you can also check out [our webpage](http://svl.stanford.edu/igibson), the [iGibson 2.0 arxiv preprint](https://arxiv.org/abs/2108.03272) and the [iGibson 1.0 arxiv preprint](https://arxiv.org/abs/2012.02924).
