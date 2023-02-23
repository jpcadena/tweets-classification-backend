"""
Password security script
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_password_hash(password: str) -> str:
    """
    Bcrypt function for password
    :param password: User password to encrypt
    :type password: str
    :return: Hashed password
    :rtype: str
    """
    return pwd_context.hash(secret=password)


async def verify_password(hashed_password, plain_password) -> bool:
    """
    Verify if secret is hashed password
    :param hashed_password: Hash password
    :type hashed_password: str
    :param plain_password: User password
    :type plain_password: str
    :return: If passwords match
    :rtype: bool
    """
    return pwd_context.verify(secret=plain_password, hash=hashed_password)
