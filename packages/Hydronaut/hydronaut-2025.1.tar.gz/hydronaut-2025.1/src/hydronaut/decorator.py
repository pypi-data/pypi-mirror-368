#!/usr/bin/env python3
"""
Decorators for running code with Hydronaut.
"""

import logging
import types
from typing import Callable

from hydronaut.run import Runner
from hydronaut.types import Decorable, Path, Runable

LOGGER = logging.getLogger(__name__)


def with_hydronaut(config_path: Path = None) -> Callable[Decorable, Runable]:
    """
    A decorator to run custom user code with Hydronaut. The user code must be
    either a class with the following methods:

    __init__(self, config):
        An initialization method that accepts the Hydra configuration object
        as its sole argument.

    __call__(self):
        A call method that returns the experiment's objective values.

    setup(self):
        An optional method that will be invoked before __call__ when the
        experiment is run. This can be used to e.g. prepare data.

    or a function that accept the Hydra configuration object as its sole
    argument and which returns the experiment's objective values.

    Args:
        config_path:
            Passed through to hydronaut.run.Runner.

    Returns:
        A callable object that runs the user code within the Hydronaut framework.
    """

    # This defines a nested decorator in order to accept the configuration file
    # path as an argument. The first decorator accepts the path and returns the
    # configured decorator that is then used to decorate the user-supplied class
    # or function.

    def _with_hydronaut(user_code: Decorable) -> Runable:
        """
        Internal decorator.
        """

        class CustomRunner(Runner):  # pylint: disable=too-few-public-methods
            """
            Create a custom Runner subclass to wrap the user code.
            """

            def get_experiment_object(self):
                # If the user code is a simple function, defer calling.
                if isinstance(user_code, types.FunctionType):

                    def exp_obj():
                        return user_code(self.config)

                # Else assume that it is a class.
                else:
                    exp_obj = user_code(self.config)
                    if not isinstance(exp_obj, Callable):
                        LOGGER.warning(
                            "%s does not create callable objects.", user_code
                        )

                return exp_obj

        return CustomRunner(config_path=config_path)

    return _with_hydronaut
