"""
fseconomy.core.data.fbo
~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the fbo data feeds.
"""
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml


def __decode_fbo(fbo: dict[str, str]) -> dict[str, Union[bool, float, int, str]]:
    """Private function to decode data representing one single FBO

    :param fbo: Python dictionary derived from FSEconomy server XML output
    :type fbo: dict
    :return: dictionary with fbo information decoded into native Python data types
    :rtype: dict
    """
    return {
        'FboId': int(fbo['FboId']),
        'Status': str(fbo['Status']).strip(),
        'Airport': str(fbo['Airport']).strip(),
        'Name': str(fbo['Name']).strip(),
        'Owner': str(fbo['Owner']).strip(),
        'Icao': str(fbo['Icao']).strip(),
        'Location': str(fbo['Location']).strip(),
        'Lots': int(fbo['Lots']),
        'RepairShop': (str(fbo['RepairShop']).strip().lower() == 'yes'),
        'Gates': int(fbo['Gates']),
        'GatesRented': int(fbo['GatesRented']),
        'Fuel100LL': int(fbo['Fuel100LL']),
        'FuelJetA': int(fbo['FuelJetA']),
        'BuildingMaterials': int(fbo['BuildingMaterials']),
        'Supplies': int(fbo['Supplies']),
        'SuppliesPerDay': int(fbo['SuppliesPerDay']),
        'SuppliedDays': int(fbo['SuppliedDays']),
        'SellPrice': float(fbo['SellPrice']),
        'Fuel100LLGal': int(fbo['Fuel100LLGal']),
        'FuelJetAGal': int(fbo['FuelJetAGal']),
        'Price100LLGal': float(fbo['Price100LLGal']),
        'PriceJetAGal': float(fbo['PriceJetAGal'])
    }


def decode(raw_data: str) -> list[dict[str, Union[bool, float, int, str]]]:
    """Decode FSEconomy FBO data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing an FBO data feed
    :type raw_data: str
    :return: list of dictionaries representing each an FBO from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    result = []
    if isinstance(data, str) and data.strip() == '':
        return result
    try:
        if 'FBO' in data['FboItems']:
            result.append(__decode_fbo(data['FboItems']['FBO']['FBO']))
        elif 'FBOs' in data['FboItems']:
            for item in data['FboItems']['FBOs']:
                result.append(__decode_fbo(item['FBO']))
        return result
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
