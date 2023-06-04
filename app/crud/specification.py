"""
This script contains abstract and concrete classes to represent
 specification objects.
These specification objects encapsulate the rules to filter or select
 specific data.
"""
from abc import ABC, abstractmethod
from typing import Any

from pydantic import EmailStr, PositiveInt


class Specification:
    """
    Abstract base class to define specifications
    """

    def __init__(self, value: Any):
        self.value: Any = value


class IdSpecification(Specification):
    """
    Specification subclass that encapsulates an ID
    """

    def __init__(self, obj_id: PositiveInt):
        super().__init__(obj_id)


class EmailSpecification(Specification):
    """
    Specification subclass that encapsulates an email address
    """

    def __init__(self, email: EmailStr):
        super().__init__(email)


class UsernameSpecification(Specification):
    """
    Specification subclass that encapsulates a username
    """

    def __init__(self, username: str):
        super().__init__(username)


class TwitterBaseSpecification(ABC):
    """
    Abstract Base Class to define specifications for a Twitter query.
    """

    @abstractmethod
    def apply(self, query: str = "") -> str:
        """
        Abstract method to apply the specification to a query
        :param query: The current query to which the specification will
         be applied
        :type query: str
        :return: The modified query with the specification applied
        :rtype: str
        """


class TwitterUsernameSpecification(TwitterBaseSpecification):
    """
    TwitterBaseSpecification subclass that encapsulates a Twitter
     username and language.
    """

    def __init__(self, username: str, lang: str = "es"):
        self.username = username
        self.lang = lang

    def apply(self, query: str = "") -> str:
        return f"{query}{self.username} lang:{self.lang}"
