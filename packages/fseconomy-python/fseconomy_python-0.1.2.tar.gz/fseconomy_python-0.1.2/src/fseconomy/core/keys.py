from typing import Optional
from ..util.hex import is_hex
from ..exceptions import FseAuthKeyError, FseDataKeyError


#: FSEconomy Access Key
ACCESS_KEY: Optional[str] = None


#: FSEconomy Service Key
SERVICE_KEY: Optional[str] = None


#: FSEconomy User Key
USER_KEY: Optional[str] = None


def validate_key(key: Optional[str]) -> bool:
    """validates a new style FSEconomy API key

    :param key: string to validate
    :type key: str
    :return: True if string is a valid API key, otherwise False
    """
    try:
        return (key is not None) and (len(key) == 16) and is_hex(key)
    except (ValueError, TypeError):
        return False


def get_data_keys() -> dict[str, str]:
    """get keys to query an FSEconomy data feed

    This function uses a set of rules to deliver a valid result even if not all
    keys are set:

    * If available, the service key is preferred over the (personal) user key.
    * If no access key has been defined, the user key is used as default.

    The function must be able to establish an authentication key (user or
    service key), and a data access key (read access or user key). In case of
    a failure, it raises either an :exc:`~fseconomy.exceptions.FseDataKeyError`
    or an :exc:`~fseconomy.exceptions.FseAuthKeyError`.

    :raises FseDataKeyError: if no valid data key can be established
    :raises FseAuthKeyError: if no valid auth key can be established

    :return: dictionary with keys
    :rtype: dict[str, str]
    """
    keys = {}

    # configure the read access key or raise an exception
    if validate_key(ACCESS_KEY):
        keys['readaccesskey'] = ACCESS_KEY
    elif validate_key(USER_KEY):
        keys['readaccesskey'] = USER_KEY
    else:
        raise FseDataKeyError

    # configure the auth key or raise an exception
    if validate_key(SERVICE_KEY):
        keys['servicekey'] = SERVICE_KEY
    elif validate_key(USER_KEY):
        keys['userkey'] = USER_KEY
    else:
        raise FseAuthKeyError

    return keys
