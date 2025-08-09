"""
fseconomy.core.data.aliases
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the aircraft aliases data feed.
"""
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml


def __decode_aliases(aircraft_alias: dict[str, str]) -> dict[str, Union[str, list[str]]]:
    """Private function to decode data representing one single aircraft alias set

    :param aircraft_alias: Python dictionary derived from FSEconomy server XML output
    :type aircraft_alias: dict
    :return: dictionary with aircraft alias information decoded into native Python data types
    :rtype: dict
    """
    result = {
        'MakeModel': str(aircraft_alias['MakeModel']).strip(),
        'Aliases': []
    }
    if 'Aliass' in aircraft_alias:
        for alias in aircraft_alias['Aliass']:
            result['Aliases'].append(str(alias).strip())
    elif 'Alias' in aircraft_alias:
        result['Aliases'].append(str(aircraft_alias['Alias']).strip())
    return result


def decode(raw_data: str) -> list[dict[str, Union[str, list[str]]]]:
    """Decode FSEconomy aircraft alias data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing an aircraft data feed
    :type raw_data: str
    :return: list of dictionaries representing each an aircraft alias set from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    result = []
    try:
        for item in data['AircraftAliasItems']['AircraftAliasess']:
            result.append(__decode_aliases(item['AircraftAliases']))
        return result
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
