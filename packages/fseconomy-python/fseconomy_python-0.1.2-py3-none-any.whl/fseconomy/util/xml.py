"""
fseconomy.util.xml
~~~~~~~~~~~~~~~~~~

This module contains a set of XML helper functions.
"""


import re
import xml.etree.cElementTree
import xml.etree.ElementTree

from ..exceptions import FseDataParseError


def _xml_char_to_python(match):
    """Convert a single XML encoded character to Python unicode character"""
    return chr(int(match.group(0).replace('&', '').replace('#', '').replace(';', '')))


def _xml_string_to_python(xml_string: str) -> str:
    """Convert an XML encoded string to a Python unicode string"""
    exp = r'&#([0-9]{1,7});'
    return re.sub(exp, _xml_char_to_python, xml_string)


def _xml_tree_to_python(tree) -> dict:
    """Convert an XML eTree structure into a Python dictionary"""
    result = {}
    if len(tree) > 0:
        result[tree.tag] = {}
        tags = set([x.tag for x in list(tree)])
        for tag in tags:
            elements = tree.findall(tag)
            if len(elements) > 1:
                result[tree.tag]['{}s'.format(tag)] = []
                for element in elements:
                    result[tree.tag]['{}s'.format(tag)].append(_xml_tree_to_python(element))
            else:
                result[tree.tag][tag] = _xml_tree_to_python(elements[0])
    else:
        if isinstance(tree.text, str):
            result = _xml_string_to_python(tree.text)
        else:
            result = tree.text
    return result


def to_python(xml_data: str) -> dict:
    """Convert raw XML string into a Python data structure

    :param xml_data: string representing XML data
    :type xml_data: str

    :raises FseDataParseError: provided text cannot be parsed

    :return: Python dictionary representing the data parsed from the XML input
    :rtype: dict
    """
    try:
        tree = xml.etree.cElementTree.fromstring(
            xml_data.strip().replace('xmlns="https://server.fseconomy.net"', '')
        )
        data = _xml_tree_to_python(tree)
    except xml.etree.ElementTree.ParseError as e:
        raise FseDataParseError(e.msg)
    return data
