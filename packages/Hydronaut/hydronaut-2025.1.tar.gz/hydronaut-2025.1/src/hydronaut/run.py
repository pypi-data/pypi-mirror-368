#!/usr/bin/env python3

# Single line for CodeMeta description.
"""Run an experiment."""

import importlib
import inspect
import logging
import numbers
import os
import subprocess
import sys
from typing import Any, Callable, Union

import hydra
import mlflow

from hydronaut.experiment import Experiment
from hydronaut.hydra.config import (
    HYDRA_VERSION_BASE,
    configure_environment,
    configure_hydra,
)
from hydronaut.hydra.omegaconf import get, get_container
from hydronaut.mlflow import MLflowRunner
from hydronaut.paths import PathManager
from hydronaut.types import OptimizationValue, Path, ensure_numeric
from hydronaut.version import VERSION

LOGGER = logging.getLogger(__name__)


class Runner:
    """
    Experiment runner.
    """

    def __init__(self, config_path: Path = None) -> None:
        """
        Args:
            config_path:
                The path to the configuration file. It is passed through to
                hydronaut.paths.get_config_path to get the main configuration
                file.
        """
        self.config_path = config_path
        self._path_manager = PathManager(config_path=config_path)
        # The Hydra configuration object, which will be set when this is run.
        self.config = None
        self.mlflow_runner = None
        self._configure_logging()

    def get_experiment_object(self) -> Experiment:
        """
        Get the experiment class specified by the configuration object.

        Returns:
            The experiment instance.

        Raises:
            ImportError:
                The module could not be found.

            AttributeError:
                The module does not contain the expected class name.
        """
        config = self.config
        exp_cls_param = config.experiment.exp_class
        try:
            exp_cls_module, exp_cls_name = exp_cls_param.split(":", 1)
        except (AttributeError, ValueError) as err:
            LOGGER.error(
                "Missing or invalid experiment class specification in %s: "
                "experiment.exp_class is %s",
                self._path_manager.config_path,
                exp_cls_param,
            )
            raise err

        importlib.import_module(exp_cls_module)
        exp_cls = getattr(sys.modules[exp_cls_module], exp_cls_name)
        LOGGER.debug("Loaded experiment class: %s", exp_cls)

        if not issubclass(exp_cls, Experiment):
            LOGGER.warning(
                "Experiment class %s.%s [%s] is not a subclass of %s.%s",
                exp_cls.__module__,
                exp_cls.__qualname__,
                inspect.getfile(exp_cls),
                Experiment.__module__,
                Experiment.__qualname__,
            )
        return exp_cls(config)

    def _configure_logging(self) -> None:
        """
        Configure initial logging. Hydra will override this when the run is
        started.
        """
        # Use the default Hydra format and level.
        logging.basicConfig(
            style="{",
            format="[{asctime:s}][{name:s}][{levelname:s}] - {message:s}",
            level=logging.INFO,
        )

    def _configure_environment(self) -> None:
        """
        Set environment variables defined in the configuration file.
        """
        env_vars = get_container(self.config, "experiment.environment", default={})
        for name, value in env_vars.items():
            os.environ[name] = value

    def _log_missing_config(self, config_path):
        LOGGER.error(
            "The expected configuration file (%s) does not exist.", config_path
        )
        if self.config_path is None:
            LOGGER.warning(
                "If you wish to use a different file, set the path in "
                "the %s environment variable.",
                self._path_manager.HYDRONAUT_CONFIG_ENV_VAR,
            )
        LOGGER.warning(
            "Relative paths are interpreted relative to %s.",
            self._path_manager.base_dir,
        )

    def _try_setup(self, obj):
        """
        Attempt to run the object's "setup" method if it has one. This is
        required because the object may be a decorated user class or function
        without a setup method.
        """
        # This is not as Pythonic as a try-except block but this avoid
        # accidentally catching exceptions raised within the setup method.
        if hasattr(obj, "setup"):
            if isinstance(obj.setup, Callable):
                obj.setup()
            else:
                LOGGER.warning('"setup" method of %s is not callable', obj)
                try:
                    obj.setup()
                except AttributeError:
                    pass

    def log_objective_value(
        self, value: Any
    ) -> Union[numbers.Real, tuple[numbers.Real]]:
        """
        Log the objective value. It will be passed through
        :py:func:`~ensure_numeric`. If the return value is a tuple, each value
        will be logged as a separate objective value.
        Args:
            value:
                The objective value(s).
        """
        value = tuple(ensure_numeric(value))
        if len(value) == 1:
            value = value[0]
            mlflow.log_metric("Objective Value", value)
        else:
            for i, val in enumerate(value, start=1):
                mlflow.log_metric(f"Objective Value {i:d}", val)
        return value

    def __call__(self, *args: Any, **kwargs: Any) -> OptimizationValue:
        """
        Run the experiment and return a value for the Optuna sweeper.

        Args:
            *args:
                Positional arguments passed through to the hydra.main function.

            **kwargs:
                Keyword arguments passed through to the hydra.main function.

        Returns:
            The value to optimize.
        """
        configure_hydra()
        config_path = self._path_manager.config_path
        if not config_path.exists():
            self._log_missing_config(config_path)
            return 1

        @hydra.main(
            version_base=HYDRA_VERSION_BASE,
            config_path=str(config_path.parent),
            config_name=config_path.stem,
        )
        def _run(config):
            """
            Internal runner function. This is defined within this method so that
            class attributes can be used as arguments to hydra.main().

            Args:
                config:
                    The Hydra configuration object. It must contain a field
                    named "experiment.class" that points to an importable Python
                    class which is a subclass of
                    hydronaut.experiment.Experiment.
            """
            LOGGER.info("Hydronaut version: %s", VERSION)
            LOGGER.info("Hydronaut configuration file: %s", config_path)
            configure_hydra()
            self.config = config
            self._configure_environment()

            with MLflowRunner(config, base_dir=self._path_manager.base_dir) as runner:
                self.mlflow_runner = runner
                # Configure the environment variables so that any experiment
                # subprocesses can invoke configure_hydra(from_env=True) to
                # re-establish the Hydra configuration. This also ensures that they
                # set the right MLflow run ID.
                configure_environment()

                self._path_manager.add_python_paths(
                    get(self.config, "experiment.python.paths")
                )

                exp = self.get_experiment_object()
                exp.mlflow_runner = runner
                self._try_setup(exp)
                obj_val = exp()
                return self.log_objective_value(obj_val)

        try:
            return _run(*args, **kwargs)
        except KeyboardInterrupt:
            return os.EX_OK


def main(*args: Any, **kwargs: Any) -> OptimizationValue:
    """
    Main function to run an experiment with the Hydra configuration.

    Args:
        *args:
            Positional arguments passed through to the hydra.main function.

        **kwargs:
            Keyword arguments passed through to the hydra.main function.

    Returns:
        The value returned by calling the runner.
    """
    return Runner()(*args, **kwargs)


def script_main() -> None:
    """
    Hydra makes some assumptions about configuration paths based on how the main
    function is called. This is a workaround for creating a script via
    pyproject.toml. It will simply invoke main() with any passed command-line
    arguments.
    """
    cmd = (sys.executable, "-m", "hydronaut.run", *sys.argv[1:])
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as err:
        sys.exit(err)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
