"""
fseconomy.util.hex
~~~~~~~~~~~~~~~~~~

This module contains a set of hex helper functions.
"""


def is_hex(value: str) -> bool:
    """validate if a string represents a number in hexadecimal format

    :param value: string to validate
    :type value: str
    :return: True if string represents a hexadecimal number, otherwise False
    :rtype: bool
    """
    try:
        _ = int(value, 16)
        return True
    except ValueError:
        return False
