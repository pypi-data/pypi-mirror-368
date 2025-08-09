"""
fseconomy.core.data.airport
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the airport static data.
"""
import csv
import io
import zipfile
from typing import Union
from ...exceptions import FseDataParseError


def __decode_airport(airport: dict[str, str]) -> dict[str, Union[float, int, str]]:
    """Private function to decode data representing one single airport

    :param airport: Python dictionary derived from FSEconomy server XML output
    :type airport: dict
    :return: dictionary with airport information decoded into native Python data types
    :rtype: dict
    """
    return {
        'icao': str(airport['icao']).strip(),
        'lat': float(airport['lat']),
        'lon': float(airport['lon']),
        'type': str(airport['type']).strip(),
        'size': int(airport['size']),
        'name': str(airport['name']).strip(),
        'city': str(airport['city']).strip(),
        'state': str(airport['state']).strip(),
        'country': str(airport['country']).strip()
    }


def decode(raw_data: bytes) -> list[dict[str, Union[int, float, str]]]:
    """Decode FSEconomy airport data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw byte data representing airport data as csv file
    :type raw_data: bytes
    :return: list of dictionaries representing each an airport from the data feed
    :rtype: list[dict]
    """
    if isinstance(raw_data, bytes) and raw_data.strip() == b'':
        return []

    result = []
    try:
        with io.BytesIO(raw_data) as df:
            reader = csv.DictReader(io.TextIOWrapper(df, encoding='iso-8859-1'))
            for row in reader:
                result.append(__decode_airport(row))
    except (KeyError, IndexError, csv.Error) as e:
        raise FseDataParseError(e)

    return result
