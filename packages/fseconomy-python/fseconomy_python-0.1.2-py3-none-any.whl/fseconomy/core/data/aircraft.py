"""
fseconomy.core.data.aircraft
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the aircraft data feeds.
"""
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml, time


def __decode_aircraft(aircraft: dict[str, str]) -> dict[str, Union[bool, float, int, str]]:
    """Private function to decode data representing one single aircraft

    :param aircraft: Python dictionary derived from FSEconomy server XML output
    :type aircraft: dict
    :return: dictionary with aircraft information decoded into native Python data types
    :rtype: dict
    """
    return {
        'SerialNumber': int(aircraft['SerialNumber']),
        'MakeModel': str(aircraft['MakeModel']).strip(),
        'Registration': str(aircraft['Registration']).strip(),
        'Owner': str(aircraft['Owner']).strip(),
        'Location': str(aircraft['Location']).strip(),
        'LocationName': str(aircraft['LocationName']).strip(),
        'Home': str(aircraft['Home']).strip(),
        'SalePrice': float(aircraft['SalePrice']),
        'SellbackPrice': float(aircraft['SellbackPrice']),
        'Equipment': str(aircraft['Equipment']).strip(),
        'RentalDry': float(aircraft['RentalDry']),
        'RentalWet': float(aircraft['RentalWet']),
        'RentalType': str(aircraft['RentalType']).strip(),
        'Bonus': float(aircraft['Bonus']),
        'RentalTime': int(aircraft['RentalTime']),
        'RentedBy': str(aircraft['RentedBy']).strip(),
        'FuelPct': float(aircraft['FuelPct']),
        'NeedsRepair': bool(int(aircraft['NeedsRepair'])),
        'AirframeTime': time.parse_hobbs(aircraft['AirframeTime']),
        'EngineTime': time.parse_hobbs(aircraft['EngineTime']),
        'TimeLast100hr': time.parse_hobbs(aircraft['TimeLast100hr']),
        'LeasedFrom': str(aircraft['LeasedFrom']).strip(),
        'MonthlyFee': float(aircraft['MonthlyFee']),
        'FeeOwed': float(aircraft['FeeOwed'])
    }


def decode(raw_data: str) -> list[dict[str, Union[bool, int, float, str]]]:
    """Decode FSEconomy aircraft data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing an aircraft data feed
    :type raw_data: str
    :return: list of dictionaries representing each an aircraft from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)

    if isinstance(data, str) and data.strip() == '':
        return []

    try:
        keys = list(data['AircraftItems'].keys())
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)

    try:
        if 'Aircraft' in keys:
            return [__decode_aircraft(data['AircraftItems']['Aircraft']['Aircraft'])]
        elif 'Aircrafts' in keys:
            result = []
            for aircraft in data['AircraftItems']['Aircrafts']:
                result.append(__decode_aircraft(aircraft['Aircraft']))
            return result
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
