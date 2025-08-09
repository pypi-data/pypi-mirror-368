#!/usr/bin/env python3

"""
Path management.
"""

import logging
import os
import pathlib
import sys

from hydronaut.types import Path

LOGGER = logging.getLogger(__name__)


class PathManager:
    """
    Path manager. This provides methods to retrieve common paths.
    """

    # The default subpath to the main configuration file. It will be
    # interpreted relative to the working directory.
    DEFAULT_CONFIG_SUBPATH = "conf/config.yaml"

    # Enviroment variable for changing the main configuration file.
    HYDRONAUT_CONFIG_ENV_VAR = "HYDRONAUT_CONFIG"

    def __init__(self, base_dir: Path = None, config_path: Path = None) -> None:
        """
        Args:
            base_dir:
                The directory relative to which to interpret paths. If None, the
                current working directory is used.
        """
        self.base_dir = (
            pathlib.Path.cwd() if base_dir is None else pathlib.Path(base_dir).resolve()
        )
        if config_path is not None:
            config_path = pathlib.Path(config_path).resolve()
        self._config_path = config_path
        LOGGER.debug("PathManager base directory: %s", self.base_dir)

    def add_python_paths(self, paths: list[Path]) -> None:
        """
        Add Paths to the Python system paths list. The resulting list will be the
        equivalent of concatenating the input paths with the current system paths.

        Args:
            paths:
                The paths to add. If relative, they are interpreted relative to the
                path given by relative_to.
        """
        if not paths:
            return
        paths = [str(self.base_dir.joinpath(path)) for path in paths]
        for path in paths:
            LOGGER.debug("adding %s to Python system path", path)
        sys.path[:] = [*paths, *sys.path]

    @property
    def config_path(self) -> pathlib.Path:
        """
        The resolved path to the main configuration file as a pathlib.Path
        object. If the path was not specified during initialization and the
        environment variable is not set, it returns the default path.
        """
        if self._config_path is not None:
            return self._config_path
        env_path = os.getenv(self.HYDRONAUT_CONFIG_ENV_VAR)
        if env_path is None:
            return self.base_dir / self.DEFAULT_CONFIG_SUBPATH
        env_path = pathlib.Path(env_path)
        if env_path.is_absolute():
            return env_path.resolve()
        return (self.base_dir / env_path).resolve()

    @property
    def config_dir(self) -> pathlib.Path:
        """
        The resolved path to the current configuration directory as a
        pathlib.Path object.
        """
        return self.config_path.parent

    def get_config_path(self, subpath: Path = None) -> pathlib.Path:
        """
        Get the path to a configuration file.

        subpath:
            The subpath relative to the configuration directory. If None,
            defaults to config.yaml.

        Returns:
            The resolved path to the configuration file as a pathlib.Path
            object.
        """
        if subpath is None:
            return self.config_path
        return self.config_dir / subpath

    def get_src_path(self, subpath: Path) -> pathlib.Path:
        """
        Get the path to a Python source file in the default source directory.

        subpath:
            The subpath relative to the source directory.

        Returns:
            The resolved path to the source file as a pathlib.Path object.
        """
        return self.base_dir / "src" / subpath
