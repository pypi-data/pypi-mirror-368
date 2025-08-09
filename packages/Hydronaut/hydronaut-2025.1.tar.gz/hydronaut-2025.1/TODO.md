---
title: TODO
---

# Hydronaut Package

* Maybe provide utility functions for generating common artifacts such as confusion matrices and learning curves. These should be library-agnostic.
* Determine how to expose output file path configuration options via the configuration file. In particular, check how to collate results from different working directories in a common MLflow session.

# Examples

* Create an sklearn example.

# Meta

* Facilitate CUDA version matching via the installation script to ensure e.g. that PyTorch is compatible with the installed version of CUDA (`nvcc -V`).
* Explain Experiment class and usage (via Sphinx documentation?).
* Maybe add helper utility for launching `mlflow ui`.

# Unit Tests

Decide on a strategy for unit testing and then implement the tests.

# MLflow

* Document usage of logging and autolog functions from the [MLflow Python API](https://www.mlflow.org/docs/latest/python_api/index.html).
