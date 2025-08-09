from typing import Union, Optional

import requests

from . import keys
from .api import DATA_FEEDS, MAINTENANCE, API_VERSIONS, DATA_FILES
from ..response import Response
from ..exceptions import FseDataFeedInvalidError, FseServerMaintenanceError, FseServerRequestError, \
    FseDataFeedParamError, FseDataFileInvalidError


def fetch(feed: str, params: Optional[dict] = None) -> Union[None, Response]:
    """Fetch data feed and parse response

    The *feed* parameter needs to represent a data feed as defined in the :mod:`~fseconomy.core.api` module.

    If the requested feed requires additional parameters, these need to be provided via the ``params`` dictionary.

    :raises FseDataFeedInvalidError: in case ``feed`` is not a valid data feed
    :raises FseDataFeedParamError: in case a required additional parameter is missing
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param feed: the data feed to fetch
    :type feed: str
    :param params: optional dictionary with additional parameters specific to the requested data feed
    :type params: dict
    :return: FSEconomy Server Response object
    :rtype: Response
    """
    # ensure params is a dictionary
    if params is None:
        params = {}

    # check if feed exists
    if feed not in DATA_FEEDS:
        raise FseDataFeedInvalidError(message="{} is not a valid FSEconomy Data Feed".format(feed))

    # check if all required params were passed
    if 'params' in DATA_FEEDS[feed]:
        for param in DATA_FEEDS[feed]['params']:
            if param not in params:
                raise FseDataFeedParamError("required parameter {} not provided".format(param))

    # create payload
    payload = {'format': 'xml', 'query': DATA_FEEDS[feed]['query'], 'search': DATA_FEEDS[feed]['search']}
    payload.update(params)
    payload.update(keys.get_data_keys())

    if 'rakey' not in DATA_FEEDS[feed] or not DATA_FEEDS[feed]['rakey']:
        del payload['readaccesskey']

    # execute request and check for a good response
    try:
        response = requests.get(API_VERSIONS['data'], params=payload)
        response.encoding = 'iso-8859-1'
    except requests.exceptions.ConnectionError:
        raise FseServerRequestError

    # detect possible server maintenance
    if MAINTENANCE in response.text:
        raise FseServerMaintenanceError

    # detect other server communication issues
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise FseServerRequestError

    # process data
    return Response(
        status=response.status_code,
        data=DATA_FEEDS[feed]['decode'](response.text),
        raw=response.text
    )


def fetch_file(file: str = '') -> Union[None, Response]:
    """Fetch static data and process response

    The *file* parameter needs to represent a data file as defined in the :mod:`~fseconomy.core.api` module.

    :raises FseDataFileInvalidError: in case ``file`` is not a valid data file
    :raises FseServerRequestError: in case the communication with the server fails
    :raises FseServerMaintenanceError: in case the server is in maintenance mode
    :raises FseDataParseError: in case the data received are malformed or cannot be parsed for other reasons

    :param file: file to be retrieved and parsed
    :type file: str
    :return: FSEconomy Server Response object
    :rtype: Response
    """
    # check if feed exists
    if file not in DATA_FILES:
        raise FseDataFileInvalidError(message="{} is not a valid FSEconomy Data File".format(file))

    # execute request and check for a good response
    try:
        response = requests.get('/'.join([API_VERSIONS['static'], DATA_FILES[file]['filename']]))
    except requests.exceptions.ConnectionError:
        raise FseServerRequestError

    # detect possible server maintenance
    if MAINTENANCE in response.text:
        raise FseServerMaintenanceError

    # detect other server communication issues
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise FseServerRequestError

    # process data
    return Response(
        status=response.status_code,
        data=DATA_FILES[file]['decode'](response.content),
        raw=response.content
    )
