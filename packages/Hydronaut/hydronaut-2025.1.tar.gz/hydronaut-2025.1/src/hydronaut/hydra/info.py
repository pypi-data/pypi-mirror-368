#!/usr/bin/env python3
"""
Hydra utility functions.
"""

from hydra.core.hydra_config import HydraConfig


def get_sweep_number() -> int:
    """
    Get the number of the current sweep.

    Returns:
        An int between in the range [0, n-1] where n is the number of sweep
        runs.
    """
    return HydraConfig.get().job.num
