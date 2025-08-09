"""
fseconomy.core.data.member
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the group member data feeds.
"""
from typing import Union
from ...exceptions import FseDataParseError, FseDataKeyError
from ...util import xml


msg_err_key = '<Error>Requires a Group ReadAccessKey.</Error>'


def __decode_member(member: dict[str, str]) -> dict[str, Union[bool, float, int, str]]:
    """Private function to decode data representing one single FBO

    :param member: Python dictionary derived from FSEconomy server XML output
    :type member: dict
    :return: dictionary with member information decoded into native Python data types
    :rtype: dict
    """
    return {
        'Name': str(member['Name']).strip(),
        'Status': str(member['Status']).strip()
    }


def decode(raw_data: str) -> list[dict[str, Union[bool, float, int, str]]]:
    """Decode FSEconomy member data

    :raises FseDataParseError: in case of malformed data provided
    :raises FseDataKeyError: in case of invalid data key provided

    :param raw_data: string with raw XML data representing a group member data feed
    :type raw_data: str
    :return: list of dictionaries representing each a group member entry from the data feed
    :rtype: list[dict]
    """
    if msg_err_key in raw_data:
        raise FseDataKeyError("This data feed requires a group access key")
    data = xml.to_python(raw_data)
    result = []
    if isinstance(data, str) and data.strip() == '':
        return result
    try:
        if 'MemberItems' in data:
            if 'Member' in data['MemberItems']:
                result.append(__decode_member(data['MemberItems']['Member']['Member']))
            elif 'Members' in data['MemberItems']:
                for item in data['MemberItems']['Members']:
                    result.append(__decode_member(item['Member']))
        return result
    except (KeyError, IndexError, ValueError) as e:
        raise FseDataParseError(e)
