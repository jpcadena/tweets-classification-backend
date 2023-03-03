"""
Specification script
"""
from abc import ABC, abstractmethod
from typing import Any

from pydantic import PositiveInt, EmailStr


class Specification:
    """
    Specification class
    """

    def __init__(self, value: Any):
        self.value: Any = value


class IdSpecification(Specification):
    """
    ID Specification class based on Specification
    """

    def __init__(self, obj_id: PositiveInt):
        super().__init__(obj_id)


class EmailSpecification(Specification):
    """
    Email Specification class based on Specification
    """

    def __init__(self, email: EmailStr):
        super().__init__(email)


class UsernameSpecification(Specification):
    """
    Username Specification class based on Specification
    """

    def __init__(self, username: str):
        super().__init__(username)


class TwitterBaseSpecification(ABC):
    """
    Base Specification class based on Abstract Base Class.
    """

    @abstractmethod
    def apply(self, query: str = "") -> str:
        """
        Apply the query
        :param query: Value of the query
        :type query: str
        :return: Query applied
        :rtype: str
        """


class TwitterUsernameSpecification(TwitterBaseSpecification):
    """
    Twitter Username Specification class that inherits from
     TwitterBaseSpecification.
    """

    def __init__(self, username: str, lang: str = "es"):
        self.username = username
        self.lang = lang

    def apply(self, query: str = "") -> str:
        return f"{query}{self.username} lang:{self.lang}"
