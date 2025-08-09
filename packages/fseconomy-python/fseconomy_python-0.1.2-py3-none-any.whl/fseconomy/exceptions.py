"""
fseconomy.exceptions
~~~~~~~~~~~~~~~~~~~~

This module contains the set of FSEconomy's exceptions.
"""

from typing import Optional


class FseBaseException(Exception):
    """Common base class for all fseconomy errors

    :param message: Optional error message
    :type message: str
    """

    def __init__(self, message: Optional[str] = None):
        super().__init__()
        if (message is None) or (message == ""):
            self.message = self.__doc__
        else:
            self.message = str(message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class FseError(FseBaseException):
    """There was an ambiguous exception while accessing the FSEconomy API"""


class FseAuthKeyError(FseBaseException):
    """Could not find a valid authentication key (user or service key)"""


class FseDataKeyError(FseBaseException):
    """Could not find a valid data access key (user or access key)"""


class FseDataFeedInvalidError(FseBaseException):
    """Invalid data feed"""


class FseDataFeedParamError(FseBaseException):
    """One or several required parameters are missing to query the requested data feed"""


class FseDataFileInvalidError(FseBaseException):
    """Invalid data file"""


class FseDataParseError(FseBaseException):
    """Unable to parse XML data received from the FSEconomy server"""


class FseServerMaintenanceError(FseBaseException):
    """The FSEconomy server is currently down for maintenance"""


class FseServerRequestError(FseBaseException):
    """Request to the FSEconomy server failed"""
