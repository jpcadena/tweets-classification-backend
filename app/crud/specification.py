"""
Specification script
"""
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
