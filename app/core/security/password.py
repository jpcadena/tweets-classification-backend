"""
Password security script
"""
from passlib.context import CryptContext

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_password_hash(password: str) -> str:
    """
    Hashes a password using the bcrypt algorithm
    :param password: the password to hash
    :type password: str
    :return: the hashed password
    :rtype: str
    """
    if not password:
        raise ValueError("Password cannot be empty or None")
    return pwd_context.hash(password)


async def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies if a plain password matches a hashed password
    :param plain_password: the plain text password to check
    :type plain_password: str
    :param hashed_password: the hashed password to compare against
    :type hashed_password: str
    :return: True if the passwords match, False otherwise
    :rtype: bool
    """
    if not plain_password:
        raise ValueError("Plain password cannot be empty or None")
    if not hashed_password:
        raise ValueError("Hashed password cannot be empty or None")
    return pwd_context.verify(plain_password, hashed_password)
