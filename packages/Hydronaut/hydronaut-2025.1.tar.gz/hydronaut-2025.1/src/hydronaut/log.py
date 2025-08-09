#!/usr/bin/env python3

"""
Logging helper functions.
"""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure logging.

    Args:
        level:
            The logging level.
    """
    logging.basicConfig(
        style="{",
        format="[{asctime}] {levelname} {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level,
    )
