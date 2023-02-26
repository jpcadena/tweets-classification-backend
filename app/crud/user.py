"""
User CRUD script
"""
from typing import Optional, Union

from pydantic import EmailStr, PositiveInt, NonNegativeInt
from sqlalchemy import select, Select, ScalarResult
from sqlalchemy.exc import NoResultFound, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.password import get_password_hash
from app.models import User
from app.schemas.user import UserSuperCreate, UserCreate, UserUpdate


async def read_user_by_id(
        user_id: int, session: AsyncSession) -> Optional[User]:
    """
    Read user information from table
    :param user_id: Unique identifier of the user
    :type user_id: int
    :param self.session: Async Session for Database
    :type self.session: AsyncSession
    :return: User information
    :rtype: User
    """
    user: User = await session.get(User, user_id)
    if not user:
        return None
    return user


async def read_user_by_username(
        username: str, session: AsyncSession) -> Optional[User]:
    """
    Read the user from the database with unique username
    :param self.session: Async Session for Database
    :type self.session: AsyncSession
    :param username: username to retrieve User from
    :type username: str
    :return: User found in database
    :rtype: User
    """
    stmt: Select = select(User).where(User.username == username)
    user: User = (await session.scalars(stmt)).one()
    if not user:
        return None
    return user


async def read_user_by_email(
        email: EmailStr, session: AsyncSession) -> Optional[User]:
    """
    Read the user from the database with unique email
    :param self.session: Async Session for Database
    :type self.session: AsyncSession
    :param email: email to retrieve User from
    :type email: EmailStr
    :return: User found in database
    :rtype: User
    """
    stmt: Select = select(User).where(User.email == email)
    user: User = None
    try:
        user = (await session.scalars(stmt)).one()
    except NoResultFound as nrf_exc:
        print(nrf_exc)
    return user


async def create_user(
        user: Union[UserCreate, UserSuperCreate],
        session: AsyncSession
) -> Union[User, str]:
    """
    Create user into the database
    :param user: Request object representing the user
    :type user: UserCreate or UserSuperCreate
    :return: Response object representing the created user in the
     database
    :rtype: User or exception
    """
    hashed_password = await get_password_hash(user.password)
    user_in = user.copy(update={"password": hashed_password})
    user_create: User = User(**user_in.dict())
    try:
        session.add(user_create)
        await session.commit()
    except IntegrityError as i_exc:
        return str(i_exc)
    created_user: User = await read_user_by_username(
        user_create.username, session)
    return created_user


async def read_users(
        offset: NonNegativeInt, limit: PositiveInt,
        session: AsyncSession
) -> Optional[list[User]]:
    """
    Read users information from table
    :param self.session: Async Session for Database
    :type self.session: AsyncSession
    :param offset: Offset from where to start returning users
    :type offset: NonNegativeInt
    :param limit: Limit the number of results from query
    :type limit: PositiveInt
    :return: User information
    :rtype: User
    """
    users: list[User] = None
    stmt: Select = select(User).offset(offset).limit(limit)
    try:
        results: ScalarResult = await session.scalars(stmt)
        users = results.all()
    except NoResultFound as nrf_exc:
        print(nrf_exc)
    return users


async def update_user(
        user_id: int, user: UserUpdate, session: AsyncSession
) -> Optional[User]:
    """
    Update user information from table
    :param user_id: Unique identifier of the user
    :type user_id: int
    :param user: Requested user information to update
    :type user: UserUpdate
    :param self.session: Async Session for Database
    :type self.session: AsyncSession
    :return: User information
    :rtype: User
    """
    found_user: User = await read_user_by_id(user_id, session)
    user_data: dict = user.dict(exclude_unset=True)
    if user_data.get('password'):
        hashed_password = await get_password_hash(user_data["password"])
        user_data["password"] = hashed_password
    # user_data["updated_at"] = datetime.now()
    for key, value in user_data.items():
        setattr(found_user, key, value)
    user_update: UserUpdate = UserUpdate(**found_user.dict())
    async with session.begin():
        session.add(user_update)
        await session.commit()
    updated_user: User = await read_user_by_id(user_id, session)
    return updated_user


async def delete_user(user_id: int, session: AsyncSession) -> bool:
    """
    Deletes a user by its id
    :param user_id: Unique identifier of the user
    :type user_id: int
    :return: True if the user is deleted; otherwise False
    :rtype: bool
    """
    found_user: User = await read_user_by_id(user_id, session)
    deleted: bool = False
    try:
        await session.delete(found_user)
        await session.commit()
        deleted = True
    except SQLAlchemyError as exc:
        print(exc, user_id)
        await session.rollback()
    return deleted
