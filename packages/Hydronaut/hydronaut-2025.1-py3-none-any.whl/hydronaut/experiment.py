#!/usr/bin/env python3
"""
Experiment base class.
"""

import logging
import pathlib
from typing import Any, Optional

import mlflow
from omegaconf import DictConfig

from hydronaut.types import Number, OptimizationValue, Path

LOGGER = logging.getLogger(__name__)


class Experiment:
    """
    Base class for experiments.

    TODO
    * Add methods for logging parameters, artefacts, etc.
    """

    def __init__(self, config: DictConfig) -> None:
        """
        Args:
            config:
                The Hydra configuration object.
        """
        self.config = config
        # This is set dynamically by Hydronaut at runtime.
        self.mlflow_runner = None

    def __call__(self) -> OptimizationValue:
        """
        Run the experiment and return the objective value(s).

        Returns:
            The objective value, or values when optimizing a multi-objective
            parameter space.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement __call__"
        )

    def setup(self) -> None:
        """
        Set up the experiment before running it (e.g. download data, generate
        files, configure databases).
        """

    @staticmethod
    def _get_artifact_uri(path: Path, subdir: Optional[Path] = None) -> str:
        """
        Get the full URI to an artifact.

        Args:
            path:
                The path to the artifact.

            subdir:
                The subpath under the URI in which the artifact is stored.

        Returns:
            The artifact URI.
        """

        if subdir is not None:
            path = pathlib.Path(subdir) / path
        return mlflow.get_artifact_uri(str(path))

    def log_artifact(
        self, local_path: Path, artifact_path: Optional[Path] = None
    ) -> None:
        """
        Wrapper around mlflow.log_artifact:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_artifact

        Args:
            local_path:
                A path to an existing artifact. The artitfact must already be
                saved to this path.

            artifact_path:
                An optional path to a directory under artifact_uri in which to
                log the artifact in MLflow.
        """
        uri = self._get_artifact_uri(local_path, subdir=artifact_path)
        local_path = str(local_path)
        if artifact_path is not None:
            artifact_path = str(artifact_path)
        LOGGER.debug("Logging artifact %s to %s", local_path, uri)
        mlflow.log_artifact(local_path, artifact_path=artifact_path)

    def log_artifacts(
        self, local_dir: Path, artifact_path: Optional[Path] = None
    ) -> None:
        """
        Wrapper around mlflow.log_artifacts:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_artifacts

        Args:
            local_dir:
                A path to a directory with artifacts.

            artifact_path:
                An optional path to a directory under artifact_uri in which to
                log the artifact in MLflow.
        """
        uri = self._get_artifact_uri(local_dir, subdir=artifact_path)
        local_dir = str(local_dir)
        if artifact_path is not None:
            artifact_path = str(artifact_path)
        LOGGER.debug("Logging artifacts in %s to %s", local_dir, uri)
        mlflow.log_artifacts(local_dir, artifact_path=artifact_path)

    def log_dict(self, dictionary: Any, artifact_file: Path) -> None:
        """
        Wrapper around mlflow.log_dict:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_dict

        Args:
            dictionary:
                A dict object to log.

            artifact_file:
                The run-relative subpath to which to save the data as a JSON or
                YAML file. The file type will be determined from the extension
                (".yaml" or ".json").
        """
        uri = self._get_artifact_uri(artifact_file)
        artifact_file = str(artifact_file)
        LOGGER.debug("Logging dict to %s", uri)
        mlflow.log_dict(dictionary, artifact_file)

    def log_figure(self, figure: Any, artifact_file: Path) -> None:
        """
        Wrapper around mlflow.log_figure:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_figure

        Args:
            figure:
                A figure to log. Check the documentation of mlflow.log_figure
                for supported figure types (e.g. Matplotlib and Plotly.py
                figures).

            artifact_file:
                The run-relative subpath to which to save the figure.
        """
        uri = self._get_artifact_uri(artifact_file)
        artifact_file = str(artifact_file)
        LOGGER.debug("Logging figure to %s", uri)
        mlflow.log_figure(figure, artifact_file)

    def log_image(self, image: Any, artifact_file: Path) -> None:
        """
        Wrapper around mlflow.log_image:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_image

        Args:
            image:
                An image to log. Check the documentation of mlflow.log_image for
                supported image types (e.g. numpy.ndarray, Pillow images).

            artifact_file:
                The run-relative subpath to which to save the image.
        """
        uri = self._get_artifact_uri(artifact_file)
        artifact_file = str(artifact_file)
        LOGGER.debug("Logging image to %s", uri)
        mlflow.log_figure(image, artifact_file)

    def log_metric(self, key: str, value: Number, step: Optional[int] = None) -> None:
        """
        Wrapper around mlflow.log_metric:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_metric

        Args:
            key:
                The metric name.

            value:
                The metric value.

            step:
                The metric step. Defaults to zero if unspecified.
        """

        LOGGER.debug("Logging metric %s = %s [step: %s]", key, value, step)
        mlflow.log_metric(key, value, step=step)

    def log_metrics(
        self, metrics: dict[str, Number], step: Optional[int] = None
    ) -> None:
        """
        Wrapper around mlflow.log_metrics:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_metrics

        Args:
            metrics:
                A dict mapping metric names to their values.

            step:
                The metric step. Defaults to zero if unspecified.
        """

        LOGGER.debug("Logging metrics %s [step: %s]", metrics, step)
        mlflow.log_metrics(metrics, step=step)

    def log_param(self, key: str, value: Any) -> None:
        """
        Wrapper around mlflow.log_param:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_param

        Args:
            key:
                The parameter name.

            value:
                The parameter value.
        """

        LOGGER.debug("Logging parameter %s = %s", key, value)
        mlflow.log_param(key, value)

    def log_params(self, params: dict[str, Any]) -> None:
        """
        Wrapper around mlflow.log_params:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_params

        Args:
            params:
                A dict mapping parameter names to their values.
        """

        LOGGER.debug("Logging parameters %s", params)
        mlflow.log_params(params)

    def log_text(self, text: str, artifact_file: Path) -> None:
        """
        Wrapper around mlflow.log_text:
        https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.log_text

        Args:
            text:
                The text to log.

            artifact_file:
                The run-relative subpath to which to save the text.
        """
        uri = self._get_artifact_uri(artifact_file)
        artifact_file = str(artifact_file)
        LOGGER.debug("Logging text to %s", uri)
        mlflow.log_text(text, artifact_file)
