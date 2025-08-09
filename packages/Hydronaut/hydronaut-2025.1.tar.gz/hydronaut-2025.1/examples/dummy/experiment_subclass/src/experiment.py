#!/usr/bin/env python3
'''
Dummy experiment.
'''

from hydronaut.experiment import Experiment


class DummyExperiment(Experiment):
    '''
    Dummy experiment.
    '''

    # This is the only method that subclasses are required to implement.
    def __call__(self):
        # Get the Hydra config object from the parent class.
        config = self.config

        # Get the experiment parameters from the config object.
        params = config.experiment.params

        # Return some numerical value based on the parameters. In a real
        # experiment, this would be a validation or test score after training
        # and fitting a model.
        return params.x * params.y * params.z
