"""
fseconomy.core.data.commodity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the commodity data feed.
"""
from typing import Union
from ...exceptions import FseDataParseError
from ...util import xml


def __decode_commodity(commodity: dict[str, str]) -> dict[str, Union[int, str]]:
    """Private function to decode data representing one single assignment

    :param commodity: Python dictionary derived from FSEconomy server XML output
    :type commodity: dict
    :return: dictionary with commodity information decoded into native Python data types
    :rtype: dict
    """
    return {
        'Location': str(commodity['Location']).strip(),
        'Type': str(commodity['Type']).strip(),
        'Amount': int(commodity['Amount'].split()[0])
    }


def decode(raw_data: str) -> list[dict[str, Union[int, str]]]:
    """Decode FSEconomy commodity data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing a commodity data feed
    :type raw_data: str
    :return: list of dictionaries representing each a commodity from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    result = []
    if isinstance(data, str) and data.strip() == '':
        return result
    try:
        if 'Commodity' in data['CommodityItems']:
            result.append(__decode_commodity(data['CommodityItems']['Commodity']['Commodity']))
        elif 'Commoditys' in data['CommodityItems']:
            for item in data['CommodityItems']['Commoditys']:
                result.append(__decode_commodity(item['Commodity']))
        return result
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
