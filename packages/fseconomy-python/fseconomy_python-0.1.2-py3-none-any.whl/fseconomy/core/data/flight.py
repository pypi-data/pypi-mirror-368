"""
fseconomy.core.data.flight
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the flight log data feeds.
"""
from datetime import datetime
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml, time


def __decode_flight(flight: dict[str, str]) -> dict[str, Union[bool, float, int, str]]:
    """Private function to decode data representing one single FBO

    :param flight: Python dictionary derived from FSEconomy server XML output
    :type flight: dict
    :return: dictionary with flight information decoded into native Python data types
    :rtype: dict
    """
    return {
        'Id': int(flight['Id']),
        'Type': str(flight['Type']).strip(),
        'Time': datetime.strptime(str(flight['Time']).strip(), "%Y/%m/%d %H:%M:%S"),
        'Distance': int(flight['Distance']),
        'Pilot': str(flight['Pilot']).strip(),
        'SerialNumber': int(flight['SerialNumber']),
        'Aircraft': str(flight['Aircraft']).strip(),
        'MakeModel': str(flight['MakeModel']).strip(),
        'From': '' if str(flight['From']).strip() == 'None' else str(flight['From']).strip(),
        'To': '' if str(flight['To']).strip() == 'None' else str(flight['To']).strip(),
        'TotalEngineTime': time.parse_hobbs(str(flight['TotalEngineTime']).strip()),
        'FlightTime': time.parse_hobbs(str(flight['FlightTime']).strip()),
        'GroupName': '' if str(flight['GroupName']).strip() == 'None' else str(flight['GroupName']).strip(),
        'Income': float(flight['Income']),
        'PilotFee': float(flight['PilotFee']),
        'CrewCost': float(flight['CrewCost']),
        'BookingFee': float(flight['BookingFee']),
        'Bonus': float(flight['Bonus']),
        'FuelCost': float(flight['FuelCost']),
        'GCF': float(flight['GCF']),
        'RentalPrice': float(flight['RentalPrice']),
        'RentalType': str(flight['RentalType']).strip(),
        'RentalUnits': time.parse_hobbs(str(flight['RentalUnits']).strip()),
        'RentalCost': float(flight['RentalCost'])
    }


def decode(raw_data: str) -> list[dict[str, Union[bool, float, int, str]]]:
    """Decode FSEconomy flight data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing a flight log data feed
    :type raw_data: str
    :return: list of dictionaries representing each a flight log entry from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    result = []
    if isinstance(data, str) and data.strip() == '':
        return result
    try:
        if 'FlightLogsByMonthYear' in data:
            if 'FlightLog' in data['FlightLogsByMonthYear']:
                result.append(__decode_flight(data['FlightLogsByMonthYear']['FlightLog']['FlightLog']))
            elif 'FlightLogs' in data['FlightLogsByMonthYear']:
                for item in data['FlightLogsByMonthYear']['FlightLogs']:
                    result.append(__decode_flight(item['FlightLog']))
        elif 'FlightLogsFromId' in data:
            if 'FlightLog' in data['FlightLogsFromId']:
                result.append(__decode_flight(data['FlightLogsFromId']['FlightLog']['FlightLog']))
            elif 'FlightLogs' in data['FlightLogsFromId']:
                for item in data['FlightLogsFromId']['FlightLogs']:
                    result.append(__decode_flight(item['FlightLog']))
        return result
    except (KeyError, IndexError, ValueError) as e:
        raise FseDataParseError(e)
