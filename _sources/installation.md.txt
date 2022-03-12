# Installation

Evaluating Embodied AI agents in BEHAVIOR requires to install three code blocks: the iGibson simulator, the BDDL library of logic language, and the benchmarking utilities (this repo).

There are two alternatives for the installation: 
1) the common and most flexible way, installing the code **manually**, from our github repositories, or with `pip`. This mode of installation is available under MacOS, Linux and Windows.
2) the fastest but less flexible way, using our **Docker** images. This second alternative is only available for Linux and Windows users. It is the preferred mode if you plan to submit to our public leaderboard on EvalAI.

### Option 1: Manual installation

In the following, we summarize the steps to install iGibson, BDDL, and the BEHAVIOR code. If you have any issues with iGibson or BDDL, please refer to the extend installation instructions in the respective repositories ([docs for iGibson installation](http://svl.stanford.edu/igibson/docs/installation.html) and [docs for BDDL installation](https://github.com/StanfordVL/bddl/blob/master/README.md)).

1) Ensure you have the all prerequisites for the installation of iGibson by following the dependencies section [here](http://svl.stanford.edu/igibson/docs/installation.html#installing-dependencies)
2) Clone all necessary repositories for the benchmark:

    a) The iGibson simulation environment: 
    ```
    git clone git@github.com:stanfordvl/iGibson.git --recursive
   ```
    b) The BEHAVIOR repository with the benchmarking utilities and baselines:
   ```
    git clone git@github.com:stanfordvl/behavior.git
   ```
3) Download and obtain access to the iGibson Dataset of Scenes and the BEHAVIOR Dataset of Objects (3D assets with physical and semantic annotations)
   1) Fill out the license agreement in this [form](https://docs.google.com/forms/d/e/1FAIpQLScPwhlUcHu_mwBqq5kQzT2VRIRwg_rJvF0IWYBk_LxEZiJIFg/viewform). This allows you to use the assets within iGibson for free for your research.
   2) After submitting the form, you will receive a key (igibson.key). Copy it into the folder that will contain the dataset, as default: `iGibson/igibson/data`
   3) Download the datasets from [here](https://storage.googleapis.com/gibson_scenes/ig_dataset.tar.gz) (size ~20GB). 
   4) Unzip the zip file into the desired folder, as default: `iGibson/igibson/data`
For more information, please visit the iGibson documentation [here](https://stanfordvl.github.io/iGibson/dataset.html#downloading-the-igibson-2-0-dataset-of-scenes-and-the-behavior-dataset-of-objects).

4) (If you haven't done it already) Create a virtual environment and activate it
    ```
    conda create -n igibson python=3.8
    conda activate igibson
    ```
5) Install the downloaded repositories in the environment
    ```
    pip install -e ./iGibson
    pip install -e ./behavior
    ```
6) Download the iGibson assets that include robot models
    ```
    python -m igibson.utils.assets_utils --download_assets
    ```
7) Run the getting started script to evaluate the installation
    ```
    python -m behavior.examples.metric_computation_example
    ```
    If you are working on your local machine, you can add `-m gui_interactive` to visualize the test on a GUI (you may want to change the rendering resolution).

Alternatively, you could install iGibson using `pip`. In that case, you can skip the steps of cloning and installing the github repositories and do it only for the `behavior` repository. 

You are now ready to evaluate your solutions on BEHAVIOR. You can also create a submission to our benchmark leaderboard at EvalAI. See [section Evaluating](evaluating.md). Finally, our code can also be used to train your policies if you are using techniques such as reinforcement learning; see [section Training](benchmarking.md).

If you run into any issues, refer to our [FAQ]() or [contact us](mailto:behavior.benchmark@gmail.com).

### Option 2: Using Docker

The following steps assume you have already installed Docker on your machine.

1) Clone this repository
    ```
    git clone git@github.com:stanfordvl/behavior.git
    ```

2) Install nvidia-docker2 following the guidelines [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)

3) Modify the provided Dockerfile (`behavior/docker/Dockerfile`) to include any additional dependencies, and your own agent. A minimal Dockerfile presents the form:
    ```
    FROM igibson/igibson:latest
    RUN git clone --depth 1 https://github.com/StanfordVL/behavior /opt/behavior
    WORKDIR /opt/behavior
    RUN pip install --no-cache-dir -e .
    WORKDIR /opt/behavior/behavior/benchmark/scripts
    ```
   You may want to change the project cloned, if you create a fork of this `behavior` repository, and add other projects to clone. You may also want to add a line to copy your own agent (and dependencies) that replaces the `CustomAgent` placeholder in `behavior/benchmark/agents/user_agent.py`
   
4) Then build your Docker container with `docker build . -t my_submission` replacing `my_submission` with the name you want to use for the Docker image.

5) Download and obtain access to the iGibson Dataset of Scenes and the BEHAVIOR Dataset of Objects (3D assets with physical and semantic annotations)
   1) Fill out the license agreement in this [form](https://docs.google.com/forms/d/e/1FAIpQLScPwhlUcHu_mwBqq5kQzT2VRIRwg_rJvF0IWYBk_LxEZiJIFg/viewform). This allows you to use the assets within iGibson for free for your research.
   2) After submitting the form, you will receive a key (igibson.key). Create a folder for the dataset and copy the key into that folder.
   3) Download the datasets from [here](https://storage.googleapis.com/gibson_scenes/ig_dataset.tar.gz) (size ~20GB). 
   4) Unzip the zip file into the created folder in step 2)
For more information, please visit the iGibson documentation [here](https://stanfordvl.github.io/iGibson/dataset.html#downloading-the-igibson-2-0-dataset-of-scenes-and-the-behavior-dataset-of-objects).

6) Run the following to evaluate the installation
    ```
    ./benchmark/scripts/test_minival_docker.sh --docker-name my_submission --dataset-path my/path/to/dataset
    ```
   where `my_submission` is the name of the docker image created before, and `my/path/to/dataset` corresponds to the path to the iGibson and BEHAVIOR Datasets

You are now ready to evaluate your solutions on BEHAVIOR. You can also create a submission to our benchmark leaderboard at EvalAI. See [section Evaluating](evaluating.md). Finally, our code can also be used to train your policies if you are using techniques such as reinforcement learning; see [section Training](benchmarking.md).
   
If you run into any issues, [contact us](mailto:behavior.benchmark@gmail.com).
