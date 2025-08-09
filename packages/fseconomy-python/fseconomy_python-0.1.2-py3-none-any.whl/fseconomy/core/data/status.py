"""
fseconomy.core.data.status
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the aircraft status data feed.
"""
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml


def __decode_status(status: dict[str, str]) -> dict[str, Union[int, str]]:
    """Private function to decode data representing one single aircraft status

    :param status: Python dictionary derived from FSEconomy server XML output
    :type status: dict
    :return: dictionary with aircraft configuration information decoded into native Python data types
    :rtype: dict
    """
    return {
        'SerialNumber': int(status['SerialNumber']),
        'Status': str(status['Status']).strip(),
        'Location': str(status['Location']).strip()
    }


def decode(raw_data: str) -> list[dict[str, Union[int, str]]]:
    """Decode FSEconomy aircraft status data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing an aircraft data feed
    :type raw_data: str
    :return: list of dictionaries representing each an aircraft configuration from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    try:
        return [__decode_status(data['AircraftStatus']['Aircraft']['Aircraft'])]
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
