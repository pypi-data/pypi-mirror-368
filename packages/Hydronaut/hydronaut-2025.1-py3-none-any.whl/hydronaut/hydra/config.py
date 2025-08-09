#!/usr/bin/env python3
"""
Structured configs for Hydra and associated helper functions.
"""

import logging
import os
import pathlib
import platform
from dataclasses import dataclass, field
from typing import Any, Optional

import hydra
import mlflow
from hydra.core.config_store import ConfigStore
from hydra.core.global_hydra import GlobalHydra
from hydra.core.hydra_config import HydraConfig
from hydra.types import RunMode
from hydra.utils import to_absolute_path
from omegaconf import DictConfig, OmegaConf

from hydronaut.hydra.resolvers import reregister

HYDRA_VERSION_BASE = "1.2"
LOGGER = logging.getLogger(__name__)

# Per-run paths, used internally to recover current filepaths.
_RUN_PATHS = {}


# This is not supported so use Any.
# DefaultsType = list[dict[str, str] | str]
DefaultsType = list[Any]


# In Python 3.10+ this can be a static method within HydronautConfig but for
# earlier versions this must be scoped outside of the class definition for the
# call to field().
def _get_hydronaut_defaults():
    """
    Factory for defaults list.
    """
    return [
        {"override /hydra/job_logging@_global_.hydra.job_logging": "colorlog"},
        {"override /hydra/hydra_logging@_global_.hydra.hydra_logging": "colorlog"},
    ]


@dataclass
class MLflowRunConfig:
    """
    Parameters for mlflow.start_run(), except for experiment_id which is set
    from the experiment name. For details, see
    https://mlflow.org/docs/latest/python_api/mlflow.html
    """

    #  experiment_id: Optional[str] = None
    run_id: Optional[str] = None
    run_name: Optional[str] = None
    nested: bool = False
    tags: Optional[dict[str, str]] = None
    description: Optional[str] = (
        "${experiment.description}-run_${hydra:job.name}_${hydra:job.num}"
    )


@dataclass
class MLflowConfig:
    """
    MLflow configuration.
    """

    start_run: Optional[MLflowRunConfig] = None


@dataclass
class PythonConfig:
    """
    Pyton configuration.
    """

    # Paths to prepend to the system path list.
    paths: Optional[list[str]] = field(default_factory=list)


@dataclass
class ExperimentConfig:  # pylint: disable=too-many-instance-attributes
    """
    Experiment configuration.
    """

    name: str
    description: str
    params: Optional[dict[str, Any]]
    exp_class: Optional[str] = None
    python: Optional[PythonConfig] = None
    mlflow: Optional[MLflowConfig] = None
    environment: Optional[dict[str, str]] = None
    defaults: Optional[DefaultsType] = field(default_factory=_get_hydronaut_defaults)


def _get_hydronaut_defaults():
    """
    Factory for defaults list.
    """
    return ["experiment/hydronaut_experiment"]


@dataclass
class HydronautConfig:
    """
    Common Hydronaut configuration.
    """

    defaults: Optional[DefaultsType] = field(default_factory=_get_hydronaut_defaults)
    #  experiment: ExperimentConfig


def _get_unique_identifier() -> str:
    """
    Get a unique process identifier.

    Returns:
        A string with the format "<node>:<pid>".
    """
    return f"{platform.node()}:{os.getpid()}"


def _reinitialize_from_environment() -> DictConfig:
    """
    Re-initialize the Hydra configuration in a subprocess from environment
    variables if uninitialized.

    Returns:
        A Hydra config object.
    """
    LOGGER.debug("Attempting to re-initialize Hydra from environment variables.")

    if GlobalHydra().is_initialized():
        LOGGER.debug("Aborting re-initialization of Hydra: already initialized.")
        return

    my_uid = _get_unique_identifier()
    main_uid = os.getenv("HYDRONAUT_MAIN_UID")
    if my_uid == main_uid:
        LOGGER.debug(
            "Aborting re-initialization of Hydra: current process is the main process."
        )
        return

    working_dir = os.getenv("HYDRONAUT_WORKING_DIR")
    os.chdir(working_dir)

    GlobalHydra.instance().clear()
    hydra.initialize_config_dir(
        version_base=HYDRA_VERSION_BASE,
        config_dir=os.getenv("HYDRONAUT_CONFIG_DIR"),
        job_name=os.getenv("HYDRONAUT_JOB_NAME"),
    )
    cfg = hydra.compose(config_name="config", return_hydra_config=True)
    HydraConfig().set_config(cfg)


def configure_hydra(from_env: bool = False) -> None:
    """
    Configure the config store, resolvers and global configs as necessary.

    Args:
        from_env:
            If True, re-initialize the Hydra configuration object from
            environment variables set by configure_environment().
    """
    store = ConfigStore.instance()
    store.store(name="hydronaut_experiment", group="experiment", node=ExperimentConfig)
    store.store(name="hydronaut_config", node=HydronautConfig)
    reregister()
    if from_env:
        _reinitialize_from_environment()


def _safe_resolve_hydra_conf(hydra_conf: DictConfig, conf: DictConfig) -> DictConfig:
    """
    Safely resolve a Hydra configuration object. This is required for simple
    runs due to a bug in Hydra's default configuration file.

    Args:
        hydra_conf:
            The Hydra configuration object.

        conf:
            The main configuration object, required for resolving interpolations.

    Returns:
        The resolved configuration object except unresolvable interpolations
        will be left in place.
    """
    # Create a copy to ensure that the original is not modified.
    conf = OmegaConf.create(OmegaConf.to_container(conf, resolve=False))

    # Replace the erroneous "hydra." interpolations with the "hydra:" resolver.
    text = OmegaConf.to_yaml(hydra_conf)
    text = text.replace("${hydra.", "${hydra:")
    hydra_conf = OmegaConf.create(text)

    # Integrate the configuration objects to ensure full resolution.
    conf.hydra = hydra_conf
    OmegaConf.resolve(conf)

    # Extract the Hydra configuration and return it.
    hydra_conf = conf.hydra
    OmegaConf.set_readonly(hydra_conf, True)
    return hydra_conf


def save_config(
    config: OmegaConf,
    path: pathlib.Path,
    resolve: bool = False,
    overwrite: bool = False,
) -> None:
    """
    Save a config to a path.

    Args:
        config:
            An OmegaConf configuration object.

        path:
            The output path.

        resolve:
            Resolve all resolvers before saving the config.
    """
    if path.exists() and not overwrite:
        LOGGER.warning("Refusing to overwrite existing file: %s", path)
    LOGGER.debug("Saving config to %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        OmegaConf.save(config=config, f=handle, resolve=resolve)
    # Make the file read-only to reduce the risk of unintentional changes if the
    # user retrieves the path via get_config_path().
    mode = path.stat().st_mode
    mode &= ~0o333
    path.chmod(mode)
    mlflow.log_artifact(path, artifact_path="hydronaut")


def configure_environment() -> None:
    """
    Save the current Hydra configuration to fully resolved OmegaConf files and
    set environment variables for subprocesses to re-initialize the current
    configuration.
    """
    if not HydraConfig.initialized():
        LOGGER.error("Unable to configure environment: Hydra is not initalized")
        return

    hydra_conf = HydraConfig.get()
    job = hydra_conf.job
    if hydra_conf.mode == RunMode.MULTIRUN:
        config_dir = pathlib.Path(hydra_conf.sweep.dir) / str(job.num)
    else:
        config_dir = hydra_conf.run.dir
    config_dir = pathlib.Path(to_absolute_path(config_dir)).resolve()

    hydra_dir = config_dir / hydra_conf.output_subdir
    conf = OmegaConf.load(hydra_dir / "config.yaml")

    # Configure MLflow
    if conf.experiment.get("mlflow") is None:
        conf.experiment.mlflow = OmegaConf.create(MLflowConfig())

    active_run = mlflow.active_run()
    if active_run is not None:
        os.environ["MLFLOW_RUN_ID"] = str(active_run.info.run_id)
    else:
        LOGGER.error("No active MLflow run")

    # Save resolved versions of the current configs for subprocesses.
    config_dir /= ".hydronaut"
    config_dir.mkdir(parents=True, exist_ok=True)
    hydra_path = config_dir / "hydra.yaml"
    save_config(
        _safe_resolve_hydra_conf(hydra_conf, conf),
        hydra_path,
        resolve=False,
        overwrite=False,
    )
    config_path = config_dir / "config.yaml"
    save_config(conf, config_path, resolve=True, overwrite=False)
    # Save the paths so that they can be retrieved via get_config_path().
    _RUN_PATHS[active_run.info.run_id] = {"hydra": hydra_path, "config": config_path}
    #  save_config(GlobalHydra().get(), config_dir / 'config.yaml', resolve=True)

    # Log Hydra configuration files.
    for hydra_config in (config_dir.parent / hydra_conf.output_subdir).glob("*"):
        mlflow.log_artifact(hydra_config, artifact_path="hydra")

    os.environ["HYDRONAUT_CONFIG_DIR"] = str(config_dir)
    os.environ["HYDRONAUT_JOB_NAME"] = str(job.name)
    os.environ["HYDRONAUT_WORKING_DIR"] = str(pathlib.Path.cwd())
    main_uid = os.getenv("HYDRONAUT_MAIN_UID")
    if main_uid is None:
        os.environ["HYDRONAUT_MAIN_UID"] = _get_unique_identifier()


def get_config_path(get_hydra: bool = False) -> pathlib.Path:
    """
    Get the path to this run's resolved configuration file. This can be useful
    for running external code that cannot be invoked directly with the
    configuration file object.

    Args:
        get_hydra:
            If True, return the path to the configuration file with the
            Hydra-specific configuration. If False (the default), return the
            experiment configuration file path.

    Returns:
        The pathlib.Path object pointing to the requested configuration file, or
        None if the path is not available. The configuration file is fully
        resolved prior to saving and can therefore be used as a normal YAML
        input file.
    """
    active_run = mlflow.active_run()
    if active_run is None:
        LOGGER.error(
            "Unable to retrieve configuration file path. No active MLflow run."
        )
        return None
    run_id = active_run.info.run_id
    paths = _RUN_PATHS.get(run_id)
    if not paths:
        LOGGER.error(
            "No configuration paths set for current MLflow run (%s) "
            "configure_environment() should be called first.",
            run_id,
        )
        return None
    return paths["hydra" if get_hydra else "config"]
