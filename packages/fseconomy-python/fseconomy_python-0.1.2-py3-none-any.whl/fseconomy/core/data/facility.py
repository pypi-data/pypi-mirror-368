"""
fseconomy.core.data.facility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the facility data feed.
"""
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml


def __decode_facility(facility: dict[str, str]) -> dict[str, Union[bool, int, str]]:
    """Private function to decode data representing one single facility

    :param facility: Python dictionary derived from FSEconomy server XML output
    :type facility: dict
    :return: dictionary with facility information decoded into native Python data types
    :rtype: dict
    """
    return {
        'Icao': str(facility['Icao']).strip(),
        'Location': str(facility['Location']).strip(),
        'Carrier': str(facility['Carrier']).strip(),
        'CommodityNames': str(facility['CommodityNames']).strip(),
        'GatesTotal': int(facility['GatesTotal']),
        'GatesRented': int(facility['GatesRented']),
        'JobsPublic': (str(facility['JobsPublic']).strip().lower() == 'yes'),
        'Destinations': str(facility['Destinations']).strip(),
        'Fbo': str(facility['Fbo']).strip(),
        'Status': str(facility['Status']).strip()
    }


def decode(raw_data: str) -> list[dict[str, Union[bool, int, str]]]:
    """Decode FSEconomy facility data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing a facility data feed
    :type raw_data: str
    :return: list of dictionaries representing each a facility from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    result = []
    if isinstance(data, str) and data.strip() == '':
        return result
    try:
        if 'Facility' in data['FacilityItems']:
            result.append(__decode_facility(data['FacilityItems']['Facility']['Facility']))
        elif 'Facilitys' in data['FacilityItems']:
            for item in data['FacilityItems']['Facilitys']:
                result.append(__decode_facility(item['Facility']))
        return result
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
