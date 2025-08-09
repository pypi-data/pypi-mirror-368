#!/usr/bin/env python3

"""
File functions.
"""

import contextlib
import io
import logging
import pathlib
import shutil
import time
from typing import Any

LOGGER = logging.getLogger(__name__)


def backup_copy(path: pathlib.Path) -> None:
    """
    Attempt to backup a copy to a timestamped path in the same directory.

    Args:
        path:
            The path to back up. If it does not exist then nothing will be done.
    """
    if path.exists():
        while True:
            timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
            new_suffix = f".{timestamp}{path.suffix}"
            backup_path = path.with_suffix(new_suffix)
            if not backup_path.exists():
                break
        LOGGER.info("Backing up %s to %s", path, backup_path)
        if path.is_dir():
            shutil.copytree(path, backup_path)
        else:
            shutil.copy2(path, backup_path)


@contextlib.contextmanager
def safe_open(
    path: pathlib.Path, *args: Any, backup: bool = False, **kwargs: Any
) -> io.TextIOBase:
    """
    Context manager for safely opening a path by first creating any missing
    parent directories and then moving any existing file to a backup path.

    Args:
        path:
            The path to open.

        backup:
            If True, backup the file at the path if it exists.

        *args:
            Positional arguments passed through to pathlib.Path.open.

        **kwargs:
            Keyword arguments passed through to pathlib.Path.open.
    Returns:
        The open file handle.
    """
    path = pathlib.Path(path).resolve()
    LOGGER.debug("opening %s", path)

    path.parent.mkdir(parents=True, exist_ok=True)

    if backup:
        backup_copy(path)

    kwargs.setdefault("encoding", "utf-8")
    with path.open(*args, **kwargs) as handle:  # pylint: disable=unspecified-encoding
        yield handle
