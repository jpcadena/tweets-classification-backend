"""
This module handles password security functions such as hashing and
 verification.
"""
from passlib.context import CryptContext

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
        raise ValueError("Password cannot be empty or None")
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
        raise ValueError("Plain password cannot be empty or None")
    if not hashed_password:
        raise ValueError("Hashed password cannot be empty or None")
    return crypt_context.verify(plain_password, hashed_password)
