"""
fseconomy.core.data.assignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains data handling functions for the assignment data feed.
"""
from typing import Union
from datetime import datetime
from ...exceptions import FseDataParseError
from ...util import xml


def __decode_assignment(assignment: dict[str, str]) -> dict[str, Union[bool, datetime, float, int, str]]:
    """Private function to decode data representing one single assignment

    :param assignment: Python dictionary derived from FSEconomy server XML output
    :type assignment: dict
    :return: dictionary with assignment information decoded into native Python data types
    :rtype: dict
    """
    return {
        'Id': int(assignment['Id']),
        'Status': str(assignment['Status']).strip(),
        'Location': str(assignment['Location']).strip(),
        'From': str(assignment['From']).strip(),
        'Destination': str(assignment['Destination']).strip(),
        'Assignment': str(assignment['Assignment']).strip(),
        'Amount': int(assignment['Amount']),
        'Units': str(assignment['Units']).strip(),
        'Pay': float(assignment['Pay']),
        'PilotFee': float(assignment['PilotFee']),
        'Expires': str(assignment['Expires']).strip(),
        'ExpireDateTime': datetime.strptime(
            str(assignment['ExpireDateTime']).strip() + '+00:00', '%Y-%m-%d %H:%M:%S%z'
        ),
        'Type': str(assignment['Type']).strip(),
        'Express': (str(assignment['Express']).strip().lower() == 'true'),
        'PtAssignment': (str(assignment['PtAssignment']).strip().lower() == 'true'),
        'Locked': str(assignment['Locked']).strip(),
        'Comment': '' if str(assignment['Comment']).strip() == 'None' else str(assignment['Comment']).strip()
    }


def decode(raw_data: str) -> list[dict[str, Union[bool, datetime, float, int, str]]]:
    """Decode FSEconomy aircraft configuration data

    :raises FseDataParseError: in case of malformed data provided

    :param raw_data: string with raw XML data representing an aircraft data feed
    :type raw_data: str
    :return: list of dictionaries representing each an aircraft configuration from the data feed
    :rtype: list[dict]
    """
    data = xml.to_python(raw_data)
    result = []
    if isinstance(data, str) and data.strip() == '':
        return result
    try:
        if 'Assignment' in data['AssignmentItems']:
            result.append(__decode_assignment(data['AssignmentItems']['Assignment']['Assignment']))
        elif 'Assignments' in data['AssignmentItems']:
            for item in data['AssignmentItems']['Assignments']:
                result.append(__decode_assignment(item['Assignment']))
        return result
    except (KeyError, IndexError) as e:
        raise FseDataParseError(e)
