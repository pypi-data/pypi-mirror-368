#!/usr/bin/env python3
"""
MLflow utility functions.
"""

import logging
import os
import pathlib
from contextlib import ExitStack
from types import TracebackType
from typing import Any, Optional, Type

import mlflow
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig, ListConfig

from hydronaut.hydra.omegaconf import get_container
from hydronaut.types import Path

LOGGER = logging.getLogger(__name__)


def _recursively_log_omegaconf_params_with_mlflow(name: str, obj: Any) -> None:
    """
    Recursively log the Hydra parameters.

    Args:
        name:
            The parameter name.

        obj:
            The parameter object.
    """
    if isinstance(obj, DictConfig):
        for key, value in obj.items():
            _recursively_log_omegaconf_params_with_mlflow(f"{name}.{key}", value)
    elif isinstance(obj, ListConfig):
        for i, value in enumerate(obj):
            _recursively_log_omegaconf_params_with_mlflow(f"{name}.{i:d}", value)
    else:
        LOGGER.debug("Logging parameter: %s = %s", name, obj)
        mlflow.log_param(name, obj)


class MLflowRunner:
    """
    Context manager to set up an MLflow run from an Omegaconf configuration
    object. When used as a context manager, it will configure the tracking URI,
    experiment, artifact location and run parameters from the configurat object.
    The context will return the MLflow active run.
    """

    def __init__(self, config: DictConfig, base_dir: Path = None) -> None:
        """
        Args:
            config:
                The Omegaconf configuration object.
        """
        self.config = config
        if base_dir is not None:
            base_dir = pathlib.Path(base_dir).resolve()
        self.base_dir = base_dir
        self.exit_stack = ExitStack()
        self.active_run_id = None

    def log_parameters(self) -> None:
        """
        Log all parameters with MLflow.
        """
        for name, value in self.config.items():
            _recursively_log_omegaconf_params_with_mlflow(name, value)

    def _set_experiment(self) -> mlflow.entities.Experiment:
        """
        Set the current experiment from the name in the configuration object.

        Returns:
            An instance of mlflow.entities.Experiment.
        """
        config = self.config

        exp_name = config.experiment.name
        LOGGER.info("MLflow experiment name: %s", exp_name)

        exp = mlflow.get_experiment_by_name(exp_name)
        if exp is None:
            exp_id = mlflow.create_experiment(name=exp_name)
            exp = mlflow.get_experiment(exp_id)
        mlflow.set_experiment(experiment_id=exp.experiment_id)

        return exp

    def _set_uris(self) -> None:
        """
        Log and set the MLflow URIs.
        """
        env_var = "MLFLOW_TRACKING_URI"
        if self.base_dir and env_var not in os.environ:
            os.environ[env_var] = (self.base_dir / "mlruns").as_uri()
        tracking_uri = mlflow.get_tracking_uri()
        LOGGER.info("MLflow tracking URI: %s", tracking_uri)

        registry_uri = os.getenv("MLFLOW_REGISTRY_URI", default=tracking_uri)
        if registry_uri:
            mlflow.set_registry_uri(registry_uri)

        LOGGER.info("MLflow registry URI: %s", mlflow.get_registry_uri())

    def _get_mlflow_run_data(self, prop, name):
        """
        Internal function for returning run data values from the active MLflow run.

        Args:
            prop:
                The RunData property to query (metrics, params or tags).

            name:
                The name of the value to return.
        """
        if prop not in ("metrics", "params", "tags"):
            raise ValueError(f"Unrecognized RunData property requested: {prop}")

        if self.active_run_id is None:
            raise RuntimeError(f"Cannot retrieve MLflow {prop} outside of active run.")

        data = mlflow.get_run(self.active_run_id).data

        value = getattr(data, prop).get(name)
        if value is None:
            LOGGER.warning(
                "The active MLflow run (%s) currently has no %s named %s",
                self.active_run_id,
                prop[:-1],  # -1 to remove the s
                name,
            )
        return value

    def get_metric(self, name):
        """
        Return the value of a metric logged during the current run.
        """
        return self._get_mlflow_run_data("metrics", name)

    def get_param(self, name):
        """
        Return the value of a parameter logged during the current run.
        """
        return self._get_mlflow_run_data("params", name)

    def __enter__(self) -> mlflow.ActiveRun:
        config = self.config
        hydra_config = HydraConfig.get()

        stack = self.exit_stack
        self._set_uris()
        self._set_experiment()

        run_kwargs = get_container(
            self.config, "experiment.mlflow.start_run", default={}
        )
        run_kwargs.setdefault("description", self.config.experiment.description)

        run_name = config.experiment.name
        job_id = hydra_config.job.get("id")
        if job_id:
            run_name = f"{run_name}-{job_id}"
        run_kwargs["run_name"] = run_name

        for key, value in sorted(run_kwargs.items()):
            LOGGER.debug("MLflow start_run parameter: %s = %s", key, value)

        active_run = stack.enter_context(mlflow.start_run(**run_kwargs))
        self.active_run_id = active_run.info.run_id

        LOGGER.info("MLflow artifact URI: %s", mlflow.get_artifact_uri())

        self.log_parameters()
        return self

    def __exit__(
        self,
        typ: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        self.exit_stack.close()
        self.active_run_id = None
