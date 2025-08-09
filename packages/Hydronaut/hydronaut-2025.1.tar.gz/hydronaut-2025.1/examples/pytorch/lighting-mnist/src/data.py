#!/usr/bin/env python3
'''
Data loaders.
'''

import logging
import pathlib

from torch.utils.data import DataLoader, random_split
from torchvision.datasets import MNIST
from torchvision import transforms
import lightning


from hydronaut.hydra.omegaconf import get, get_container
from hydronaut.hydra.config import configure_hydra


LOGGER = logging.getLogger(__name__)


class MNISTDataModule(lightning.LightningDataModule):
    '''
    MNIST data loader.
    '''
    def __init__(self, config):
        '''
        Args:
            config:
                Omegaconf configuration object.
        '''
        super().__init__()
        self.config = config
        self.mnist_train = None
        self.mnist_val = None
        self.mnist_test = None

        self.dataloader_kwargs = get_container(
            self.config,
            'experiment.params.dataloader',
            default={}
        )

    def setup(self, stage=None):
        '''
        Setup method.
        '''
        # Required when the worker is run in a thread.
        configure_hydra(from_env=True)
        data_dir = str(
            pathlib.Path(
                get(
                    self.config,
                    'experiment.params.data_directory',
                    default='tmp'
                )
            ).resolve()
        )

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])

        mnist_train = MNIST(data_dir, train=True, download=True, transform=transform)
        self.mnist_test = MNIST(data_dir, train=False, download=True, transform=transform)

        self.mnist_train, self.mnist_val = random_split(mnist_train, [55000, 5000])

    def train_dataloader(self):
        '''
        train_dataloader method.
        '''
        return DataLoader(self.mnist_train, **self.dataloader_kwargs)

    def val_dataloader(self):
        '''
        val_dataloader method.
        '''
        return DataLoader(self.mnist_val, **self.dataloader_kwargs)

    def test_dataloader(self):
        '''
        test_dataloader method.
        '''
        return DataLoader(self.mnist_test, **self.dataloader_kwargs)
