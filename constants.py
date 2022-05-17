##################################################################################################
#                                 MIT Licence (C) 2022 Cubicpath@Github                          #
##################################################################################################
"""Constant values for the program."""

__all__ = (
    'COUNTRY',
    'EXECUTABLE_NAME',
    'XP_BOOST_ONLY',
)

from typing import Final

# Booleans

XP_BOOST_ONLY:  Final[bool] = True

# Strings

COUNTRY:           Final[str] = 'GB'
EXECUTABLE_NAME:   Final[str] = 'geckodriver.exe'
