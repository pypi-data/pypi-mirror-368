#!/usr/bin/env python3
"""
Hydra resolvers.
"""

import logging
import multiprocessing
import pathlib
import urllib.parse

try:
    import torch
except ImportError:
    torch = None
from hydra.core.utils import setup_globals as hydra_setup_globals
from hydra.utils import get_original_cwd
from omegaconf import OmegaConf

LOGGER = logging.getLogger(__name__)


def _parse_args(args):
    """
    Parse resolver arguments.

    Args:
        args:
            A list of strings with the format "key=value" or just "key". Keys
            without a value will be assigned the value of True. If a value is
            given, the words "true", "false", "none" and "null" will be
            converted to the Python values True, False, None and None,
            respectively, regardless of case.

    Returns:
        A dict mapping the keys to the parsed values.
    """
    kwargs = {}
    val_map = {"true": True, "false": False, "none": None, "null": None}
    for arg in args:
        try:
            key, value = arg.split("=", 1)
        except ValueError:
            kwargs[arg] = True
        else:
            kwargs[key] = val_map.get(value.lower(), value)
    return kwargs


def get_cwd(*args):
    """
    The current working directory from which the main function was launched.

    Args:
        resolve:
            If True, resolve symlinks in the path.

        uri:
            If True, return the path as a URI.

    Returns:
        The resulting string.
    """
    try:
        path = pathlib.Path(get_original_cwd())
    except ValueError:
        path = pathlib.Path.cwd()
    kwargs = _parse_args(args)

    if kwargs.get("resolve", False):
        path = path.resolve()

    if kwargs.get("uri", False):
        return path.as_uri()

    return str(path)


def _get_divisor(args):
    """
    Internal function to handle optional divisor to some resolvers.
    """
    if len(args) > 0:
        divisor = int(args[0])
        if divisor > 0:
            return divisor
    return 1


def get_n_cpu(*args):
    """
    Get the number of available CPUs. Optionally accept an integer argument
    which will be used to divide the result.

    Args:
        *args:
            An optional single integer argument. If given, the number of CPUs
            will be divided by this number.

    Returns:
        The number of available CPUs. If a divisior is given then this will
        always return a value of at least 1.
    """
    n_cpu = multiprocessing.cpu_count()
    return max(n_cpu // _get_divisor(args), 1)


def get_n_gpu_pytorch(*args):
    """
    Get the number of available PyTorch GPUs. Optionally accept an integer
    argument which will be used to divide the result.

    Args:
        *args:
            An optional single integer argument. If given, the number of CPUs
            will be divided by this number.

    Returns:
        The number of available PyTorch GPUs. If the number is greater than 0
        than a value of at least 1 will always be returned when an optional
        divisor is given.
    """
    if torch is None:
        LOGGER.warning("PyTorch must be installed to get the number of PyTorch GPUs")
        return 0
    n_gpu = torch.cuda.device_count()
    if n_gpu < 1:
        return 0
    return max(n_gpu // _get_divisor(args), 1)


def register() -> dict[str, str]:
    """
    Register custom resolvers.

    Returns:
        A dict mapping resolver names to their descriptions.
    """

    resolvers = {}
    for name, func in (
        ("url_quote", urllib.parse.quote),
        ("cwd", get_cwd),
        ("n_cpu", get_n_cpu),
        ("n_gpu_pytorch", get_n_gpu_pytorch),
        ("max", max),
        ("min", min),
    ):
        LOGGER.debug("Registing resolver %s", name)
        OmegaConf.register_new_resolver(name, func)
    return resolvers


def reregister() -> None:
    """
    Reregister custom and Hydra resolvers. This is necessary due to a bug in the
    process launcher.
    """
    if not OmegaConf.has_resolver("n_cpu"):
        register()
    if not OmegaConf.has_resolver("hydra"):
        hydra_setup_globals()
