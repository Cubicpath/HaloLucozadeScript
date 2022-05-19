##################################################################################################
#                                 MIT Licence (C) 2022 Cubicpath@Github                          #
##################################################################################################
"""Utility functions for program."""

__all__ = (
    'wait',
)

from random import randint
from time import sleep


def wait(min_seconds: int | float, max_seconds: int | float | None = None) -> None:
    """Wait a random amount of time between min_seconds and max_seconds.

    If max_seconds is None, wait exactly min_seconds.
    """
    if max_seconds is None:
        sleep(min_seconds)
    else:
        sleep(randint(int(min_seconds * 1000), int(max_seconds * 1000)) / 1000)
