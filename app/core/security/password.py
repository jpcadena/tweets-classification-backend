"""
This module handles password security functions such as hashing and
 verification.
"""
import logging

from passlib.context import CryptContext

logger: logging.Logger = logging.getLogger(__name__)
crypt_context: CryptContext = CryptContext(
    schemes=["bcrypt"], deprecated="auto")


async def get_password_hash(password: str) -> str:
    """
    Hash a password using the bcrypt algorithm
    :param password: The password to hash
    :type password: str
    :return: The hashed password
    :rtype: str
    """
    if not password:
        error: str = "Password cannot be empty or None"
        logger.error(error)
        raise ValueError(error)
    return crypt_context.hash(password)


async def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies if a plain text password matches a hashed password
    :param plain_password: The plain text password to verify
    :type plain_password: str
    :param hashed_password: The hashed password to compare against
    :type hashed_password: str
    :return: True if the passwords match, False otherwise
    :rtype: bool
    """
    if not plain_password:
        error: str = "Plain password cannot be empty or None"
        logger.error(error)
        raise ValueError(error)
    if not hashed_password:
        hash_error: str = "Hashed password cannot be empty or None"
        logger.error(hash_error)
        raise ValueError(hash_error)
    return crypt_context.verify(plain_password, hashed_password)
