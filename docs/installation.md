# Installation

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
    c) Download the BEHAVIOR data bundle including the BEHAVIOR Dataset of Objects and ... from [form]().
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

If you run into any issues, refer to our [FAQ]() or [contact us](mailto:behavior@gmail.com).