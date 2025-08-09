"""
fseconomy.core.data.config
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the aircraft config data feed.
"""
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml


def __decode_config(config: dict[str, str]) -> dict[str, Union[float, int, str]]:
    """Private function to decode data representing one single aircraft configuration

    :param config: Python dictionary derived from FSEconomy server XML output
    :type config: dict
    :return: dictionary with aircraft configuration information decoded into native Python data types
    :rtype: dict
    """
    return {
        'MakeModel': str(config['MakeModel']).strip(),
        'Crew': int(config['Crew']),
        'Seats': int(config['Seats']),
        'CruiseSpeed': int(config['CruiseSpeed']),
        'GPH': int(config['GPH']),
        'FuelType': int(config['FuelType']),
        'MTOW': int(config['MTOW']),
        'EmptyWeight': int(config['EmptyWeight']),
        'Price': float(config['Price']),
        'Ext1': int(config['Ext1']),
        'LTip': int(config['LTip']),
        'LAux': int(config['LAux']),
        'LMain': int(config['LMain']),
        'Center1': int(config['Center1']),
        'Center2': int(config['Center2']),
        'Center3': int(config['Center3']),
        'RMain': int(config['RMain']),
        'RAux': int(config['RAux']),
        'RTip': int(config['RTip']),
        'Ext2': int(config['Ext2']),
        'Engines': int(config['Engines']),
        'EnginePrice': float(config['EnginePrice']),
        'ModelId': int(config['ModelId']),
        'MaxCargo': int(config['MaxCargo'])
    }


def decode(raw_data: str) -> list[dict[str, Union[float, int, str]]]:
    """Decode FSEconomy aircraft configuration data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing an aircraft data feed
    :type raw_data: str
    :return: list of dictionaries representing each an aircraft configuration from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    result = []
    try:
        for item in data['AircraftConfigItems']['AircraftConfigs']:
            result.append(__decode_config(item['AircraftConfig']))
        return result
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
