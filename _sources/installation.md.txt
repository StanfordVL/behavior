# Installation

Evaluating Embodied AI agents in BEHAVIOR requires to install three code blocks: the iGibson simulator, the BDDL library of logic language, and the benchmarking utilities (this repo).

There are two alternatives for the installation: 
1) the common and most flexible way, installing the github repositories (or pip installing) manually. This is available under MacOS, Linux and Windows.
2) the fastest but less flexible using a Docker image. This second alternative is only available for Linux and Windows users. It is the preferred mode if you plan to submit to our public leaderboard on EvalAI.

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
   4) Unzip the zip file into the desired folder

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

If you run into any issues, refer to our [FAQ]() or [contact us](mailto:behavior.benchmark@gmail.com).

### Option 2: Using Docker

**This section needs to be updated. Until that is done, please, follow the instructions above or modify the instructions below to adapt to the new Docker images.**

1) Clone this repository
    ```
    git clone git@github.com:stanfordvl/behavior.git
    ```

2) Install nvidia-docker2 following the guidelines [here](https://github.com/nvidia/nvidia-docker/wiki/Installation-(version-2.0))

3) Modify the provided Dockerfile to include any additional dependencies, and your own agent. A minimal Dockerfile presents the form:
    ```
    FROM stanfordvl/behavior:latest
    ENV PATH /miniconda/envs/gibson/bin:$PATH
    
    ADD benchmark/agents/agent.py /agent.py
    ADD benchmark/agents/random_agent.py /random_agent.py
    ADD benchmark/agents/rl_agent.py /rl_agent.py
    ADD benchmark/behavior_benchmark.py /behavior_benchmark.py
    
    ADD benchmark/scripts/submission.sh /submission.sh
    WORKDIR /
    ```
   Then build your Docker container with `docker build . -t my_submission` replacing `my_submission` with the name you want to use for the Docker image.

4) Download and obtain access to the BEHAVIOR Dataset of Objects (3D assets with physical and semantic annotations). If you already did this before, for example because you also installed the repositories, you can skip this step. Otherwise:
    
    a) Fill out the license agreement in this [form](https://docs.google.com/forms/d/e/1FAIpQLScPwhlUcHu_mwBqq5kQzT2VRIRwg_rJvF0IWYBk_LxEZiJIFg/viewform). This allows you to use the assets within iGibson for free for your research.
    b) After submitting the form, you will receive a key (igibson.key). Create a folder for the dataset and copy the key into that folder.
    c) Download the datasets from [here](https://storage.googleapis.com/gibson_scenes/ig_dataset.tar.gz) (size ~20GB). 
    d) Unzip the zip file into the created folder
    
5) You are ready to train and test your solutions, or create a submission to EvalAI. See [Section Training and Evaluating](benchmarking.md)
   
If you run into any issues, refer to our [FAQ]() or [contact us](mailto:behavior.benchmark@gmail.com).
