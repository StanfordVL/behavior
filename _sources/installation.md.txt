# Installation

Evaluating Embodied AI agents in BEHAVIOR requires to install three code blocks: the iGibson simulator, the BDDL library of logic language, and the benchmarking utilities (this repo).

There are two alternatives for the installation: 
1) the common and most flexible way, installing the github repositories (or pip installing) manually. This is available under MacOS, Linux and Windows.
2) the fastest but less flexible using a Docker image. This second alternative is only available for Linux and Windows users. It is the preferred mode if you plan to submit to our public leaderboard on EvalAI.

### Option 1: Manual installation of dependencies and code

In the following, we summarize the steps to install iGibson, BDDL, and the BEHAVIOR code. If you have any issues with iGibson or BDDL, please refer to the extend installation instructions in the respective repositories ([docs for iGibson installation](http://svl.stanford.edu/igibson/docs/installation.html) and [docs for BDDL installation](https://github.com/StanfordVL/bddl/blob/master/README.md)).

1) Ensure you have the all prerequisites for the installation of iGibson by following the dependencies section [here](http://svl.stanford.edu/igibson/docs/installation.html#installing-dependencies)
2) Clone all necessary repositories for the benchmark:

    a) The iGibson simulation environment: 
    ```
    git clone git@github.com:stanfordvl/iGibson.git --recursive
   ```
    b) The BDDL logic language:
   ```
    git clone git@github.com:stanfordvl/bddl.git
   ```
    c) The BEHAVIOR repository with the benchmarking utilities and baselines:
   ```
    git clone git@github.com:stanfordvl/behavior.git
   ```
3) Download and obtain access to the BEHAVIOR Dataset of Objects (3D assets with physical and semantic annotations) 
    
    a) Accept the license agreement filling the [form](https://forms.gle/GXAacjpnotKkM2An7). This allows you to use the assets within iGibson for free for your research.
    
    b) You will receive a encryption key (`igibson.key`). Move the key into the data folder of the iGibson repository, `iGibson/igibson/data`.
    
    c) Download the BEHAVIOR data bundle including the BEHAVIOR Dataset of Objects and the iGibson2 Dataset of scenes from [form]().
    
    d) Decompress the BEHAVIOR data bundle:
    ```
    unzip behavior_data_bundle.zip -d iGibson/igibson/data
    ```
4) (If you haven't done it already) Create a virtual environment and activate it
    ```
    conda create -n igibson python=3.8
    conda activate igibson
    ```
5) Install the downloaded repositories in the environment
    ```
    pip install -e ./iGibson
    pip install -e ./bddl
    pip install -e ./behavior
    ```
6) Download the iGibson assets that include robot models
    ```
    python -m igibson.utils.assets_utils --download_assets
    ```
7) Run the getting started script to evaluate the installation
    ```
    python iGibson/igibson/examples/behavior/behavior_env_metrics.py -m headless
    ```
    If you are working on your local machine, you can drop the `-m headless` flag and visualize the test on a GUI.

Alternatively, you could install iGibson and BDDL using `pip`. In that case, you can skip the steps of cloning and installing their github repositories and do it only for the `behavior` repository.

If you run into any issues, refer to our [FAQ]() or [contact us](mailto:behavior.benchmark@gmail.com).

### Option 2: Using Docker

**This section needs to be updated. Until that is done, please, follow the instructions above or modify the instructions below to adapt to the new Docker images.**

1) Clone this repository
    ```
    git clone git@github.com:stanfordvl/behavior.git
    ```

2) Install nvidia-docker2 following the guidelines [here](https://github.com/nvidia/nvidia-docker/wiki/Installation-(version-2.0))

3) Modify the provided Dockerfile to include any additional dependencies and your own agent. A minimal Dockerfile presents the form:
    ```
    FROM stanfordvl/behavior:latest
    ENV PATH /miniconda/envs/igibson/bin:$PATH
    
    ADD benchmark/agents/agent.py /agent.py
    ADD benchmark/agents/random_agent.py /random_agent.py
    ADD benchmark/agents/rl_agent.py /rl_agent.py
    ADD benchmark/behavior_benchmark.py /behavior_benchmark.py
    
    ADD benchmark/scripts/submission.sh /submission.sh
    WORKDIR /
    ```
   Then build your Docker container with `docker build . -t my_submission` replacing `my_submission` with the name you want to use for the Docker image.

4) Download and obtain access to the BEHAVIOR Dataset of Objects (3D assets with physical and semantic annotations) 
    
    a) Accept the license agreement filling the [form](https://forms.gle/GXAacjpnotKkM2An7). This allows you to use the assets within iGibson for free for your research.
    
    b) You will receive a encryption key (`igibson.key`). Move the key into the main folder of this repository `behavior`.
    
    c) Download the BEHAVIOR data bundle including the BEHAVIOR Dataset of Objects and the iGibson2 Dataset of scenes from [form]().
    
    d) Decompress the BEHAVIOR data bundle into this folder:
    ```
    unzip behavior_data_bundle.zip -d behavior
    ```
   
If you run into any issues, refer to our [FAQ]() or [contact us](mailto:behavior.benchmark@gmail.com).
