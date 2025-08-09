#!/usr/bin/env python3
"""
PyTorch Lightning experiments.
"""

import logging

import lightning
import mlflow.pytorch
from lightning.pytorch.callbacks import Callback
from omegaconf import DictConfig

from hydronaut.experiment import Experiment
from hydronaut.hydra.omegaconf import get_container
from hydronaut.types import OptimizationValue

LOGGER = logging.getLogger(__name__)


class LightningExperiment(Experiment):
    """
    Experiment class for PyTorch Lightning experiments.

    The configuration file should include a dictionary under
    "experiment.params.trainer" that contains PyTorch Lighting Trainer keyword
    arguments and their values. These will be passed through to the Trainer. See
    https://lightning.ai/docs/pytorch/stable/common/trainer.html#trainer-class-api
    for details.
    """

    def __init__(
        self,
        config: DictConfig,
        model_cls: lightning.LightningModule,
        data_module_cls: lightning.LightningDataModule,
        callback_classes: list[Callback] = None,
    ) -> None:
        """
        Args:
            config:
                Same as Experiment.__init__().

            model_cls:
                A subclass of LightningModule.

            data_module_cls:
                A subclass of LightningDataModule.

            callback_classes:
                An optional list of Callback subclasses.

        model_cls, data_module_cls and all classes in callback_classes should
        all accept a single configuration object as a parameter to their
        __init__ methods.
        """
        super().__init__(config)

        # Configure the model and data.
        self.model = model_cls(config)
        self.data = data_module_cls(config)

        # Instantiate the callback classes for the trainer.
        if callback_classes:
            self.callbacks = [c_cls(config) for c_cls in callback_classes]
        else:
            self.callbacks = []

        # Instantiate the trainer.
        params = config.experiment.params
        trainer_kwargs = get_container(params, "trainer", default={}, resolve=True)
        trainer_kwargs["callbacks"] = self.callbacks
        self.trainer = lightning.Trainer(**trainer_kwargs)

        # Configure MLflow logging.
        # https://github.com/mlflow/mlflow/blob/eb3588abb55032838b1ff5af1b7d660f2b826dee/examples/pytorch/MNIST/mnist_autolog_example.py
        if self.trainer.global_rank == 0:
            mlflow.pytorch.autolog()

        # Dict for storing arbitrary result values.
        self.results = {}

    def get_objective_value(self) -> OptimizationValue:
        """
        Return an objective value for the optimizer. This must be overridden in
        subclasses. It can use any of the attributes of this class such as the
        LightningModule instance or any of the optional Callback instances.

        Returns:
            A numerical value or tuple of numerical values for the optimizer.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not override get_objective_value()"
        )

    def __call__(self):
        """
        Fit and test the model using the trainer and return the objective value.
        """
        self.trainer.fit(self.model, datamodule=self.data)
        self.results["test"] = self.trainer.test(datamodule=self.data)
        return self.get_objective_value()
