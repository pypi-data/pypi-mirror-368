---
title: PyTorch Lighting MNIST Example README
---

# Synopsis

This example shows how to create a PyTorch Lightning experiment using the [PLExperiment class](src/torch/lightning/experiment.py). The [MNISTExperiment subclass](src/experiment.py) only requires the user to define subclasses of PyTorch Lightning's LightningModule and LightningDataModule along with a `get_objective_value` method to extract an objective value for the Optuna optimizer.

The [configuration file](conf/config.yaml) uses the [Hydra Optuna sweeper plugin](https://hydra.cc/docs/plugins/optuna_sweeper/)  with the [Optuna TPE sampler](https://optuna.readthedocs.io/en/stable/reference/samplers/index.html) be default. The sampler can be changed by modifying the value of the override at the top of the file.

This model is intentionally complex to showcase how the Optuna sweeper can be used to change parameters such as the number of convolution layers and their sizes. The parameter space is defined under `hydra.sweeper.params` and all value overrides are inserted into `experiment.params` for easy use within the model. The Optuna Sweeper plugin page describes the supported functions for exploring the parameter space (range, interval, choice) and modifiers using e.g. log distributions.

The configuration file is commented to clarify which fields set parameters such as the number of Optuna trials, the number of DataLoader workers, the number of epochs, the batch size, etc. By default, the model will invoke a single PyTorch Lighting model at a time and allow it to delegate the workload automatically (e.g. using DDP for systems with multiple GPUs). The DataLoader is configured to run with `experiment.params.dataloader.num_workers` processes.

Because of this model's simplicity, the speedup from using multiple GPUs is offset by the time to dispatch the model to multiple GPUs and collate the results after each epoch. However, more complex models will benefit from this approach.

To instead use a single job per GPU, the following changes can be made to the configuration file:

* Add `override hydra/launcher: joblib` above `_self_` in the defaults list.
* Set `hydra.sweeper.n_jobs` to `${n_gpu_torch:}`.
* Set `experiment.params.dataloader.num_workers` to 0.
* Set `experiment.params.trainer.devices` to 1.

Note that the console output will be noisy with this approach due to several concurrent processes updating progress bars simultaneously.


# Usage

~~~sh
hydronaut-run --multirun
~~~
