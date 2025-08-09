from typing import Optional

from .core import keys
from .util.hex import is_hex


def set_service_key(key: Optional[str] = None):
    """set the FSEconomy service key

    :param key: string representing a valid FSEconomy service key
    """
    if keys.validate_key(key):
        keys.SERVICE_KEY = key


def set_access_key(key: Optional[str] = None):
    """set the FSEconomy read access key

    :param key: string representing a valid FSEconomy access key
    """
    if keys.validate_key(key):
        keys.ACCESS_KEY = key


def set_user_key(key: Optional[str] = None):
    """set the FSEconomy user key

    :param key: string representing a valid FSEconomy user key
    """
    if keys.validate_key(key):
        keys.USER_KEY = key
