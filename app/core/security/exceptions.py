"""
This module defines custom exception classes for the Core Security
 package.
"""
from sqlalchemy.exc import SQLAlchemyError


class DatabaseException(SQLAlchemyError):
    """
    Database Exception class
    """

    def __init__(self, message: str):
        super().__init__(message)


class ServiceException(Exception):
    """
    Service Layer Exception class
    """

    def __init__(self, message: str):
        super().__init__(message)


class NotFoundException(Exception):
    """
    Not Found Exception class
    """

    def __init__(self, message: str):
        super().__init__(message)
