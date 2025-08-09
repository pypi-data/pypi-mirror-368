#!/usr/bin/env python3
'''
Dummy function with a decorator.
'''

import sys

from hydronaut.decorator import with_hydronaut


@with_hydronaut(config_path='conf/config.yaml')
def main(config):
    '''
    Main function that accepts the configuration object passed by the decorator.
    It is based on the dummy Experiment subclass example.
    '''
    # Get the experiment parameters from the config object.
    params = config.experiment.params

    # Return some numerical value based on the parameters. In a real
    # experiment, this would be a validation or test score after training
    # and fitting a model.
    return params.x * params.y * params.z


if __name__ == '__main__':
    sys.exit(main())  # pylint: disable=no-value-for-parameter
