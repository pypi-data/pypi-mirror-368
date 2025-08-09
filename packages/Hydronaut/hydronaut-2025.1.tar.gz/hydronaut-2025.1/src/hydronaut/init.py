#!/usr/bin/env python3

# Single line for CodeMeta description.
"""Initialize a directory with default files for Hydronaut."""

import argparse
import logging

from hydronaut.file import safe_open
from hydronaut.log import configure_logging
from hydronaut.paths import PathManager

LOGGER = logging.getLogger()


class Initializer:
    """
    Initialize a directory with default files.
    """

    def __init__(self) -> None:
        self.path_manager = PathManager()
        self.config_path = self.path_manager.get_config_path()
        self.pargs = None

    def parse_args(self, args: list[str] = None) -> None:
        """
        Parse the command-line arguments with argparse.

        Args:
            args:
                The list of arguments to parse. If None, the arguments are taken
                from the current system invocation.

        Returns:
            The parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description="Generate default files for a Hydronaut project."
        )
        parser.add_argument(
            "-s",
            "--sweeper",
            choices=("optuna",),
            help=(
                """
                Use the given Hydra sweeper.
            """
            ),
        )
        parser.add_argument(
            "-l",
            "--launcher",
            choices=("joblib",),
            help=(
                """
                Use the given Hydra launcher.
            """
            ),
        )
        self.pargs = parser.parse_args(args)

    def run(self, args: list[str] = None) -> None:
        """
        Process command-line arguments and generate the requested files.

        Args:
            args:
                Passed through to parse_args().
        """
        self.parse_args(args=args)
        self.create_config()
        self.create_experiment()

    def create_config(self) -> None:
        """
        Create the configuration file.
        """
        pargs = self.pargs
        config_path = self.config_path
        LOGGER.info("creating %s", config_path)
        with safe_open(config_path, "w", backup=True) as handle:
            handle.write(
                """
# This is the main Hydra configuration file for the current Hydronaut project.
# Hydra uses OmegaConf to load its configuration files so all OmegaConf features
# are supported. For details, read the respective documentation.
#
# https://hydra.cc/docs/intro/
# https://pypi.org/project/omegaconf/

# Default values are used to override sections of the configuration file with
# values from other files.
defaults:
  # Ensure type-checking for the experiment section. This is specific to
  # Hydronaut. This will also set some defaults for logging configuration.
  - hydronaut_config""".strip()
            )

            if pargs.sweeper == "optuna":
                handle.write(
                    """

  # Use the Optuna sweeper. This is configured in the hydra.sweeper section
  # below.
  - override hydra/sweeper: optuna
  # Set the default sampler to TPE. For other supported samplers, see
  # https://optuna.readthedocs.io/en/stable/reference/samplers/index.html
  - override hydra/sweeper/sampler: tpe"""
                )

            if pargs.launcher == "joblib":
                handle.write(
                    """

  # Use the joblib launcher. This is configured in the hydra.launcher section.
  # https://hydra.cc/docs/1.2/plugins/joblib_launcher/
  - override hydra/launcher: joblib"""
                )

            handle.write(
                """

  # Optionally enabled colors in log messages.
  - override hydra/job_logging: colorlog
  - override hydra/hydra_logging: colorlog

  # Required to ensure that some of the above settings work correctly.
  - _self_

# Hydra configuration.
hydra:
  # Uncomment this to enable the Hydra multirun with the sweeper by default.
  # Without this option, it is necessary to pass the --multirun option at
  # invocation.
  # mode: MULTIRUN

  # Hydra job configuration: https://hydra.cc/docs/configure_hydra/job/
  job:
    # Set environment variables such as OMP_NUM_THREADS. These variables are set
    # later than those in the "experiment.environment" field below.
    env_set:
        # OMP_NUM_THREADS: ${n_cpu:}
"""
            )
            handle.write(
                """
  # Sweeper parameter. These depend on the currently configured sweeper.
  sweeper:"""
            )

            if pargs.sweeper == "optuna":
                handle.write(
                    """
    # Optuna sweeper parameters.
    # See https://hydra.cc/docs/plugins/optuna_sweeper/ for details.

    # The way to optimize the objective function returned by the Experiment
    # subclass (maximize or minimize). This may also be a list if the objective
    # function returns multiple values.
    direction: maximize

    # Set the study name here. The default simply appends "-study" to the
    # experiment's name.
    study_name: ${experiment.name}-study

    # The study storage backend as an SQLAlchemy storage backend URL:
    # https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
    # If unset or null then the study will use impersistant in-memory storage.
    # storage: sqlite:///${url_quote:"${cwd:}"}/optuna.db


    # The number of Optuna trials.
    n_trials: 40

    # The number of jobs to use. For naive single-CPU models use ${n_cpu:}. For
    # other models such as those based on PyTorch-lightning, set this to 1.
    n_jobs: ${n_cpu:}

    # Sampler options.
    sampler:
      # Set the seed for reproducibility.
      seed: 123"""
                )

            handle.write(
                """
    # Parameters to sweep. These should append or override values in
    # experiment.params. For details of the available sweeper options such as
    # range, interval and choice, consult the following documentation:
    # https://hydra.cc/docs/plugins/optuna_sweeper/
    params:
      # Add a parameter that will be swept over the integer range [1,10]. This
      # will be accessible from Python via
      # config.experiment.params.swept_param_1.
      ++experiment.params.swept_param_1: range(1, 10)"""
            )

            if pargs.launcher == "joblib":
                handle.write(
                    """
  # See https://hydra.cc/docs/plugins/joblib_launcher/ for details and further
  # options.
  launcher:
    # Use as many jobs as there are CPUs. This is essentially equivalent to
    # ${n_cpu:}
    n_jobs: -1"""
                )

            handle.write(
                """

experiment:
  # Experiment name.
  name: My Experiment

  # Experiment description.
  description: Placeholder experiment.

  # The Experiment subclass to use for the experiment. This is a string with the
  # format "<module>:<class name>". "<module>" must be the name of a module that
  # Python can import and it must contain a subclass of
  # hydronaut.experiment.Experiment with the name "<class name>". The default is
  # set to the class in the generated in the src/experiment.py file.
  exp_class: experiment:MyExperiment

  # Experiment parameters used in the Experiment subclass to configure the
  # model, data and everything else. If a sweeper is used, then the values will
  # be appended to this section before the config object is passed to the
  # Experiment subclass.
  params:
    # Example parameter that will be accessible from Python via
    # config.experiment.params.fixed_param_1.
    fixed_param_1: 5

  # Python configuration.
  python:
    # System search paths relative to the working directory. Use this to add
    # custom modules to the Python system path without having to manually
    # configure PYTHONPATH or sys.path.
    paths:
        - src

  # Environment variables. This section may be used to configure MLflow
  # tracking, artifact and registry servers, for example. It should map
  # environment variable names to their values, as strings.
  # For example, see
  # https://mlflow.org/docs/latest/tracking.html
  # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables
  environment:
    # Examples of common variables:
    # MLFLOW_TRACKING_URI:
    # MLFLOW_TRACKING_USERNAME:
    # MLFLOW_TRACKING_PASSWORD:
    # MLFLOW_S3_ENDPOINT_URL:
    # AWS_ACCESS_KEY_ID:
    # AWS_SECRET_ACCESS_KEY:
    # AWS_DEFAULT_REGION:
    # AWS_SESSION_TOKEN:

  # MLflow configuration
  mlflow:
    # Run parameters. These are passed through directly to
    # mlflow.start_run().See the documentation for details:
    # https://mlflow.org/docs/latest/python_api/mlflow.html
    start_run:
      # Set a description for the run. This defaults to the value of the
      # "experiment.description" field above. It can be customized here to
      # include run-specific parameters, for example.
      description: ${experiment.description}
      # Set optional arbitrary tags. These could contain parameter values, dates
      # and times, the hostname of the machine on which the run was executed,
      # the name of the user who executed the run, etc.
      tags:
        framework: Hydronaut
"""
            )

    def create_experiment(self) -> None:
        """
        Create a placeholder experiment subclass.
        """
        source_path = self.path_manager.get_src_path("experiment.py")
        LOGGER.info("creating %s", source_path)
        with safe_open(source_path, "w", backup=True) as handle:
            handle.write(
                """#!/usr/bin/env python3
'''
Placeholder experiment.
'''

from hydronaut.experiment import Experiment


class MyExperiment(Experiment):
    '''
    Placeholder experiment to serve as a starting point.
    '''

    # This is the only required definition to use the Hydronaut framework. The
    # __call__ method should encapsulate your workflow from data loading to
    # model fitting and then return one or more metrics for the optimizer.
    #
    # All parameters should be set in the config object that Hydra creates from
    # your YAML configuration file (conf/config.yaml).
    def __call__(self):
        # The configuration object.
        config = self.config
        # The parameters set in the experiment.params section.
        params = config.experiment.params

        # Use the configured parameters.
        fixed_param_1 = params.fixed_param_1
        # "get()" is used here because the parameter will only be set when Hydra
        # is in the multirun mode.
        swept_param_1 = params.get('swept_param_1', 1)

        # Return a value.
        return fixed_param_1 * swept_param_1"""
            )


def main(args: list[str] = None) -> None:
    """
    Initialize a directory with default files.
    """
    configure_logging()
    initializer = Initializer()
    initializer.run(args=args)


if __name__ == "__main__":
    main()
