"""
fseconomy.response
~~~~~~~~~~~~~~~~~~

This module contains the FSEconomy Server Response class.
"""
import http
from typing import Optional, Any, Union


class Response:
    """FSEconomy Server Response

    :param status: HTTP status code sent by the server
    :type status: int
    :param data: data received from the server represented by native Python data types
    :type data: Any
    :param raw: raw data received from the server
    :type raw: Union[str, bytes]
    """

    def __init__(self, status: int = 0, data: Optional[Any] = None, raw: Optional[Union[str, bytes]] = None):
        self._status: int = status
        self._data: Any = data
        self._raw: Optional[Union[str, bytes]] = raw

    @property
    def status(self) -> int:
        """HTTP status code sent by the server"""
        return self._status

    @status.setter
    def status(self, value: int):
        self._status = http.HTTPStatus(int(value))

    @property
    def data(self) -> Optional[Any]:
        """Data received from the server decoded into native Python data types"""
        return self._data

    @data.setter
    def data(self, value: Optional[Any] = None):
        self._data = value

    @property
    def raw(self) -> Optional[Union[str, bytes]]:
        """Data received from the server as raw string or bytes"""
        return self._raw

    @raw.setter
    def raw(self, value: Optional[Union[str, bytes]] = None):
        self._raw = value

    @property
    def binary(self) -> bool:
        """Raw data is binary"""
        return isinstance(self._raw, bytes)
