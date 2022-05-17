##################################################################################################
#                                 MIT Licence (C) 2022 Cubicpath@Github                          #
##################################################################################################
"""Utility functions for program."""

__all__ = (
    'wait_between',
)

from random import randint
from time import sleep


def wait_between(min_seconds: int | float, max_seconds: int | float) -> None:
    """Wait a random amount of time between a and b."""
    sleep(randint(int(min_seconds * 1000), int(max_seconds * 1000)) / 1000)
