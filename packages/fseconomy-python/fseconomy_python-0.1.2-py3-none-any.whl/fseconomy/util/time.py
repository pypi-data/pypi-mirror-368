"""
fseconomy.util.time
~~~~~~~~~~~~~~~~~~~

This module contains a set of time data conversion and helper functions.
"""
from ..exceptions import FseDataParseError


def parse_hobbs(hobbs: str) -> float:
    """Convert an FSE hobbs string into a float value in hours.

    Example:

    >>> parse_hobbs('50:30')
    50.5

    :raises FseDataParseError: in case submitted string is not a valid hobbs string

    :param hobbs: FSEconomy hobbs string
    :type hobbs: str
    :return: hours represented by the hobbs string
    :rtype: float
    """
    result: float = 0.0
    try:
        parts = hobbs.split(':')
        if len(parts) > 0:
            result += float(parts[0])
        if len(parts) > 1:
            if float(parts[1]) >= 60.0:
                raise ValueError("Incorrect minutes value >= 60")
            result += float(parts[1]) / 60.0
        if len(parts) > 2:
            if float(parts[2]) >= 60.0:
                raise ValueError("Incorrect seconds value >= 60")
            result += float(parts[2]) / 3600.0
    except (ValueError, IndexError, AttributeError) as e:
        raise FseDataParseError(e)
    return result
