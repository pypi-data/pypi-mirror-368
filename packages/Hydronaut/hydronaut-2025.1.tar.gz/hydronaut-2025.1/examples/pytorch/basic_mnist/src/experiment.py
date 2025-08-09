#!/usr/bin/env python3
'''
PyTorch Basic MNIST Example Experiment.
'''

import torch

from hydronaut.experiment import Experiment

# Import the main function from the adapted example code.
from model import main  # pylint: disable=wrong-import-order


class MyExperiment(Experiment):  # pylint: disable=too-few-public-methods
    '''
    Invoke the code in mode.py
    '''

    def __call__(self):
        # The configuration object is an attribute of the parent class.
        # Pass it to the main function which was adapted to use it and
        # return the mode, the average loss and the accuracy.
        model, avg_loss, accuracy = main(self.config)

        # Optionally save the model.
        if self.config.experiment.params.meta.save_model:
            torch.save(model.state_dict(), 'mnist_cnn.pt')
            self.log_artifact('mnist_cnn.pt', 'model')

        # Log both metrics
        self.log_metric('average loss', avg_loss)
        self.log_metric('accuracy', accuracy)

        # Return the accuracy as the objective value to maximize.
        # We could just as well minimize the average loss, or even
        # return both values to optimize both simultaneous. We'll see
        # this in a later tutorial.
        return accuracy
