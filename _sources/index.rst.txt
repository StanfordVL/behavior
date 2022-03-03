.. BEHAVIOR documentation master file, created by
   sphinx-quickstart on Tue Nov 19 14:38:54 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the documentation of BEHAVIOR
========================================

In this documentation, you will find information to use BEHAVIOR to train, develop and evaluate your solutions.
You will have to install and use iGibson, our open source simulation environment, and the BEHAVIOR Dataset of Objects (more in the [installation instructions](installation.md)).
You will also find details about the benchmark setup such as the [embodiments available](agents.md), the control and sensing alternatives, the metrics, and the [activities](activities.md).
This documentation includes also useful information to get started with [examples](examples.md) and [baselines](baselines.md).

.. toctree::
   :maxdepth: 1
   :caption: Introduction

   intro.md
   installation.md
   benchmarking.md
   baselines.md

.. toctree::
   :maxdepth: 1
   :caption: Components of BEHAVIOR

   agents.md
   setups.md
   activities.md
   vr_demos.md
   objects.md
   metrics.md

.. toctree::
   :maxdepth: 1
   :caption: API

   apidoc/modules.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
