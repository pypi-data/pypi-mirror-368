#!/usr/bin/env python3
'''
Hydra-configured convolutional network for MNIST.
'''

import logging

import torch
import lightning
from torch.nn import functional as F


from hydronaut.hydra.info import get_sweep_number
from hydronaut.hydra.omegaconf import get_container


LOGGER = logging.getLogger(__name__)


class MNISTClassifier(lightning.LightningModule):  # pylint: disable=too-many-ancestors
    '''
    Model generator based on an Optuna Trial.
    '''

    def _add_convolutional_layers(self):
        '''
        Add the sequential convolution layers.

        Returns:
            The output dimension.
        '''
        params = self.config.experiment.params
        input_dim = params.input_dim

        # Variable number of convolutional layers with pooling and drop-out.
        layers = []
        n_layers = params.conv_layers
        current_depth = 1
        size = input_dim

        for i in range(1, n_layers + 1):
            conv_depth = params.get(f'conv_depth_{i}')
            conv_dim = params.get(f'conv_dim_{i}')
            pool = params.get(f'pool_{i}')
            drop = params.get(f'drop_{i}')

            # Size check to ensure minimal dimensions after convolution and
            # pooling.
            size = (size + pool - conv_dim) // pool
            if size <= 1:
                LOGGER.warning(
                    'requested dimensions too small in sweep %d',
                    get_sweep_number()
                )
                break

            layers.extend((
                torch.nn.Conv2d(current_depth, conv_depth, (conv_dim, conv_dim)),
                torch.nn.ReLU(),
                torch.nn.MaxPool2d(pool),
                torch.nn.Dropout(p=drop)
            ))
            current_depth = conv_depth
        layers.append(torch.nn.Flatten(start_dim=-3))
        self.conv_layers = torch.nn.Sequential(*layers)

        # Calculate the number of elements after the convolution layers.
        with torch.no_grad():
            zeros = torch.zeros(  # pylint: disable=no-member
                1, 1, input_dim, input_dim, device=self.device
            )
            return self.conv_layers.forward(zeros).numel()

    def __init__(self, config):
        '''
        Args:
            config:
                Omegaconf configuration object.
        '''
        super().__init__()
        self.config = config
        params = config.experiment.params

        lin1_in = self._add_convolutional_layers()
        lin1_out = params.lin1_out
        lin1_drop = params.lin1_drop

        self.lin1 = torch.nn.Linear(lin1_in, lin1_out)
        # Per-input bias.
        self.register_parameter(
            name='lin1_bias',
            param=torch.nn.Parameter(
                # pylint: disable=no-member
                torch.zeros(lin1_in, requires_grad=True, device=self.device)
            )
        )
        self.lin1_act = torch.nn.ReLU()
        self.lin1_drop = torch.nn.Dropout(p=lin1_drop)

        self.lin2 = torch.nn.Linear(lin1_out, 10)
        self.lin2_act = torch.nn.Softmax(dim=-1)

    def forward(self, x):  # pylint: disable=invalid-name,arguments-differ
        '''
        Parent override.
        '''
        x = self.conv_layers(x)
        x -= self.lin1_bias
        x = self.lin1(x)
        x = self.lin1_act(x)
        x = self.lin1_drop(x)
        x = self.lin2(x)
        x = self.lin2_act(x)
        return x

    def configure_optimizers(self):
        '''
        Parent override.
        '''
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=float(self.config.experiment.params.learning_rate)
        )
        return optimizer

    def cross_entropy_loss(self, logits, labels):
        '''
        Loss function.
        '''
        return F.nll_loss(logits, labels)

    def log_with_config_args(self, *args, **kwargs):
        '''
        Wrapper around log() that auto-appends keyword arguments from the
        config.
        '''
        more_kwargs = get_container(self.config, 'experiment.params.log', default={})
        if more_kwargs:
            kwargs.update(more_kwargs)
        super().log(*args, **kwargs)

    def training_step(self, batch, _batch_idx):  # pylint: disable=arguments-differ
        '''
        Parent override.
        '''
        x, y = batch  # pylint: disable=invalid-name
        logits = self.forward(x)
        loss = self.cross_entropy_loss(logits, y)
        self.log('train_loss', loss.item())
        return loss

    def validation_step(self, batch, _batch_idx):  # pylint: disable=arguments-differ
        '''
        Parent override.
        '''
        x, y = batch  # pylint: disable=invalid-name
        logits = self.forward(x)
        loss = self.cross_entropy_loss(logits, y)
        self.log_with_config_args('val_loss', loss.item())
        return loss

    def test_step(self, batch, _batch_idx):  # pylint: disable=arguments-differ
        '''
        Parent override.
        '''
        x, y = batch  # pylint: disable=invalid-name
        logits = self.forward(x)
        loss = self.cross_entropy_loss(logits, y)
        self.log_with_config_args('test_loss', loss.item())
        return loss
