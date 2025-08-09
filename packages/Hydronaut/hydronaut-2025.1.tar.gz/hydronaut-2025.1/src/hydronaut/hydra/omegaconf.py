#!/usr/bin/env python3
"""
Omegaconf utility functions.
"""

import importlib
import inspect
import logging
from typing import Any, Optional

from omegaconf import DictConfig, OmegaConf  # pylint: disable=import-self

LOGGER = logging.getLogger(__name__)


def get(config: DictConfig, name: str, default: Any = None) -> Any:
    """
    Get a nested parameter such as foo.bar.baz from an Omegaconf configuration
    object, with default value.

    Args:
        config:
            The configuration object.

        name:
            The nested parameter name. It will be split on ".".

        default:
            An optional default value. Default: None

    Returns:
        The parameter value, or the default value if any of the nested values
        are missing or the resulting value is None.
    """
    value = config
    for component in name.split("."):
        try:
            value = getattr(value, component)
        except AttributeError:
            return default
    if value is None:
        return default
    return value


def get_container(
    config: DictConfig, name: str, *, default: Any = None, resolve: bool = True
) -> Any:
    """
    A wrapper around get() that transforms the result with OmegaConf.to_container.

    Args:
        config:
            Same as get().

        name:
            Same as get().

        default:
            Same as get().

        resolve:
            Passed through to to_container(). If True, the resolvers will be
            resolved before creating the container.

    Returns:
        The container returned by a call to OmegaConf.to_conainer if the result
        of get() is an OmegaConf configuration object, otherwise the value
        returned by get().
    """
    result = get(config, name, default=default)
    if OmegaConf.is_config(result):
        result = OmegaConf.to_container(result, resolve=resolve)
    return result


def set_globals(
    config: DictConfig, name: str, *, module: Optional[str] = None, resolve: bool = True
) -> None:
    """
    Set or update global values in a loaded module with values from the
    configuration object. This is mainly useful for speeding up calculations
    that would otherwise suffer from repeated lookups up the values within the
    OmegaConf configuration object.

    Args:
        config:
            Same as get().

        name:
            Same as get().

        module:
            An optional module or module name. If not given then the module from
            which this function was invoked is used.

        resolve:
            Same as get_container().
    """
    values = get_container(config, name, default={}, resolve=resolve)
    if not values:
        return
    if module is None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
    elif isinstance(module, str):
        module = importlib.import_module(module)
    elif not inspect.ismodule(module):
        raise ValueError(
            f"The value of the module parameter must be a module, a string or None, "
            f"not {type(module)}"
        )
    for key, value in values.items():
        LOGGER.debug("Setting %s.%s to %s", module.__name__, key, value)
        setattr(module, key, value)
