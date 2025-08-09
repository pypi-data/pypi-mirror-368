#!/usr/bin/env python3
'''
Dummy function with a decorator.
'''

import logging
import sys

from hydronaut.decorator import with_hydronaut


LOGGER = logging.getLogger(__name__)


@with_hydronaut(config_path='conf/config.yaml')
class Dummy():
    '''
    A dummy class to show the user of the Hydronaut decorator. It is based on
    the dummy Experiment subclass example.
    '''
    def __init__(self, config):
        '''
        Args:
            config:
                The configuration object which will be passed from the decorator
                at runtime.
        '''
        self.config = config

    def setup(self):
        '''
        The setup method will be called before __call__ at runtime. It can be
        used to prepare data for the experiment or perform other actions that
        need only be done once.
        '''
        LOGGER.info('called setup()')

    def __call__(self):
        # Get the experiment parameters from the config object.
        params = self.config.experiment.params

        # Return some numerical value based on the parameters. In a real
        # experiment, this would be a validation or test score after training
        # and fitting a model.
        return params.x * params.y * params.z


if __name__ == '__main__':
    sys.exit(Dummy())  # pylint: disable=no-value-for-parameter
