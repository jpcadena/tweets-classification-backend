"""
Scope schema
"""
from enum import Enum


class Scope(str, Enum):
    """
    Enum representing different scopes
    """
    ACCESS_TOKEN: str = "access_token"
    REFRESH_TOKEN: str = "refresh_token"
