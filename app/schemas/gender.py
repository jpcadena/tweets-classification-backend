"""
Gender schema
"""
from enum import Enum


class Gender(str, Enum):
    """
    Gender class that inherits from built-in Enum
    """
    MALE: str = 'male'
    FEMALE: str = 'female'
    OTHER: str = 'other'
