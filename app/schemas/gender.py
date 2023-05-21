"""
Gender schema
"""
from enum import Enum


class Gender(str, Enum):
    """
    Enum representing different gender options
    """
    MALE: str = "male"
    FEMALE: str = "female"
    OTHER: str = "other"
