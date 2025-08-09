#!/usr/bin/env python3
"""
Type definitions and functions.
"""

import logging
import numbers
import pathlib
from collections.abc import Generator, Iterable
from typing import Any, Callable, Tuple, Union

from omegaconf import DictConfig

LOGGER = logging.getLogger(__name__)


# Generic number type.
Number = Union[int, float]

# Optimization value for the Optuna sweeper returned by hydronaut.run.Runner.__call__.
OptimizationValue = Union[Number, Tuple[Number, ...]]

# Generic path type for functions that can handle both pathlib Paths or strings.
Path = Union[str, pathlib.Path]

# A type supported by the decorator.
Decorable = Union[
    Callable[DictConfig, OptimizationValue],
    Callable[DictConfig, Callable[[], OptimizationValue]],
]

# The return type of the decorator.
Runable = Callable[[], OptimizationValue]


def ensure_numeric(value: Any) -> Generator[numbers.Real]:
    """
    Convert values to numeric values. If the value is iterable, then the
    function will be recursively applied to its elements.

    Args:
        value:
            The value to check.

    Returns:
        A generator over numeric values (instances of numbers.Real). Values that
        could not be converted will be returned as NaN values.
    """
    if isinstance(value, Iterable):
        for val in value:
            yield from ensure_numeric(val)
        return
    if isinstance(value, numbers.Real):
        yield value
        return
    try:
        yield float(value)
    except ValueError:
        LOGGER.warning("Failed to convert %s to numeric value.", value)
        yield float("nan")
