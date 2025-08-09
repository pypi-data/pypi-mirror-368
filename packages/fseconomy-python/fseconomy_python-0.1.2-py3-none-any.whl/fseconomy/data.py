"""
fseconomy.data
~~~~~~~~~~~~~~

This module contains public functions to access the FSEconomy Data Feeds.
"""
from .response import Response
from .core.fetch import fetch, fetch_file


def aircraft_status_by_registration(registration: str) -> Response:
    """Aircraft Status by Registration

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param registration: the aircraft registration as string
    :type registration: str
    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft status by registration', {'aircraftreg': registration})


def aircraft_configs() -> Response:
    """Aircraft Configurations

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft configs')


def aircraft_aliases() -> Response:
    """Aircraft Aliases

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft aliases')


def aircraft_for_sale() -> Response:
    """Aircraft for Sale

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft for sale')


def aircraft_by_makemodel(makemodel: str) -> Response:
    """Aircraft by MakeModel

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param makemodel: the make/model as string
    :type makemodel: str
    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft by makemodel', {'makemodel': makemodel})


def aircraft_by_ownername(ownername: str) -> Response:
    """Aircraft by Owner Name

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param ownername: the owner name as string
    :type ownername: str
    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft by ownername', {'ownername': ownername})


def aircraft_by_registration(registration: str) -> Response:
    """Aircraft by Registration

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param registration: the aircraft registration as string
    :type registration: str
    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft by registration', {'aircraftreg': registration})


def aircraft_by_id(serialnumber: int) -> Response:
    """Aircraft by Id

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param serialnumber: the aircraft numeric ID
    :type serialnumber: int
    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft by id', {'serialnumber': serialnumber})


def aircraft_by_key() -> Response:
    """Aircraft by Key

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('aircraft by key')


def assignments_by_key() -> Response:
    """Assignments by Key

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('assignments by key')


def commodities_by_key() -> Response:
    """Commodities by Key

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('commodities by key')


def facilities_by_key() -> Response:
    """Facilities by Key

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('facilities by key')


def fbos_by_key() -> Response:
    """FBOs by Key

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('fbos by key')


def fbos_for_sale() -> Response:
    """FBOs for Sale

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('fbos for sale')


def fbo_monthly_summary_by_icao(month: int, year: int, icao: str) -> Response:
    """FBO Monthly Summary by ICAO

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param month: the month as numeric value (1 = January, 12 = December)
    :type month: int
    :param year: the year as numeric value
    :type year: int
    :param icao: the (FSE) ICAO code of the airport or airfield the FBO is at
    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('fbo monthly summary by icao', {'month': month, 'year': year, 'icao': icao})


def flight_logs_by_key_month_year(month: int, year: int) -> Response:
    """Flight Logs By Key Month Year

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param month: the month as numeric value (1 = January, 12 = December)
    :type month: int
    :param year: the year as numeric value
    :type year: int

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('flight logs by key month year', {'month': month, 'year': year})


def flight_logs_by_reg_month_year(month: int, year: int, registration: str) -> Response:
    """Flight Logs By Reg Month Year

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param month: the month as numeric value (1 = January, 12 = December)
    :type month: int
    :param year: the year as numeric value
    :type year: int
    :param registration: the aircraft registration as string
    :type registration: str

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('flight logs by reg month year', {'month': month, 'year': year, 'aircraftreg': registration})


def flight_logs_by_serialnumber_month_year(month: int, year: int, serialnumber: int) -> Response:
    """Flight Logs By serialnumber Month Year

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param month: the month as numeric value (1 = January, 12 = December)
    :type month: int
    :param year: the year as numeric value
    :type year: int
    :param serialnumber: the aircraft numeric ID
    :type serialnumber: int

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('flight logs by serialnumber month year', {'month': month, 'year': year, 'serialnumber': serialnumber})


def flight_logs_by_key_from_id(fromid: int) -> Response:
    """Flight Logs By Key From Id (Limit 500)

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param fromid: the flight id to start from
    :type fromid: int

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('flight logs by key from id', {'fromid': fromid})


def flight_logs_by_key_from_id_for_all_group_aircraft(fromid: int) -> Response:
    """Flight Logs By Key From Id for ALL group aircraft (Limit 500)

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param fromid: the flight id to start from
    :type fromid: int

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('flight logs by key from id for all group aircraft', {'fromid': fromid, 'type': 'groupaircraft'})


def flight_logs_by_reg_from_id(fromid: int, registration: str) -> Response:
    """Flight Logs By Reg From Id (Limit 500)

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param fromid: the flight id to start from
    :type fromid: int
    :param registration: the aircraft registration as string
    :type registration: str

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('flight logs by reg from id', {'aircraftreg': registration, 'fromid': fromid})


def flight_logs_by_serialnumber_from_id(fromid: int, serialnumber: int) -> Response:
    """Flight Logs By serialnumber From Id (Limit 500)

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param fromid: the flight id to start from
    :type fromid: int
    :param serialnumber: the aircraft numeric ID
    :type serialnumber: int

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('flight logs by serialnumber from id', {'fromid': fromid, 'serialnumber': serialnumber})


def group_members() -> Response:
    """Group Members

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons
    :raises FseDataKeyError: in case of invalid data access key (group key required)

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch('group members')


def fse_icao_data() -> Response:
    """FSE ICAO Data

    :raises FseDataFileInvalidError: in case ``file`` is not a valid data file
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :return: Response object with data retrieved from the FSEconomy server
    :rtype: Response
    """
    return fetch_file('airports')
