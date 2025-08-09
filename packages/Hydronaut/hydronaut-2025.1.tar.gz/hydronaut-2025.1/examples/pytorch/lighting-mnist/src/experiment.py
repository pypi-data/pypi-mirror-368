#!/usr/bin/env python3
'''
MNIST experiment.
'''

import logging

from omegaconf import DictConfig

from hydronaut.lightning.experiment import LightningExperiment

from model import MNISTClassifier  # pylint: disable=wrong-import-order,no-name-in-module
from data import MNISTDataModule  # pylint: disable=wrong-import-order

LOGGER = logging.getLogger(__name__)


class MNISTExperiment(LightningExperiment):  # pylint: disable=too-few-public-methods
    '''
    MNIST experiment with PyTorch Lightning.
    '''

    # The PyTorch Lighting Experiment class only requires the user to define a
    # model and a dataloader.
    def __init__(self, config: DictConfig):
        super().__init__(
            config,
            MNISTClassifier,
            MNISTDataModule
        )

    def get_objective_value(self):
        # Return the value logged by the LightningModule instance in the
        # test_step method.
        return self.results['test'][-1]['test_loss']
