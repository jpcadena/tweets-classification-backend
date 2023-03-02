"""
User CRUD script
"""
import logging
from typing import Optional, Union

from fastapi import Depends
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import ScalarResult, Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import logging_config
from app.core.decorators import with_logging, benchmark
from app.core.security.exceptions import DatabaseException
from app.core.security.password import get_password_hash
from app.crud.filter import IndexFilter, UniqueFilter, get_index_filter, \
    get_unique_filter
from app.crud.specification import EmailSpecification, IdSpecification, \
    UsernameSpecification
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserSuperCreate, UserUpdate

logging_config.setup_logging()
logger: logging.Logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repository class for User.
    """

    def __init__(self, session: AsyncSession, index_filter: IndexFilter,
                 unique_filter: UniqueFilter):
        self.session: AsyncSession = session
        self.index_filter: IndexFilter = index_filter
        self.unique_filter: UniqueFilter = unique_filter
        self.model: User = User

    async def read_by_id(self, _id: IdSpecification) -> User:
        """
        Reads the user by its id
        :param _id:
        :type _id: IdSpecification
        :return: User instance
        :rtype: User
        """
        try:
            user: User = await self.index_filter.filter(
                _id, self.session, self.model)
        except SQLAlchemyError as db_exc:
            raise DatabaseException(str(db_exc)) from db_exc
        return user

    async def read_by_username(
            self, username: UsernameSpecification) -> Optional[User]:
        """
        Read the user by its username
        :param username: The username to search
        :type username: UsernameSpecification
        :return: User instance
        :rtype: User
        """
        try:
            user: User = await self.unique_filter.filter(
                username, self.session, self.model)
        except SQLAlchemyError as db_exc:
            raise DatabaseException(str(db_exc)) from db_exc
        return user

    async def read_by_email(self, email: EmailSpecification) -> Optional[User]:
        """
        Read the user by its email
        :param email: The email to search
        :type email: EmailSpecification
        :return: User instance
        :rtype: User
        """
        try:
            user: User = self.unique_filter.filter(
                email, self.session, self.model)
        except SQLAlchemyError as db_exc:
            raise DatabaseException(str(db_exc)) from db_exc
        return user

    @with_logging
    @benchmark
    async def read_users(
            self, offset: NonNegativeInt, limit: PositiveInt,
    ) -> list[User]:
        """
        Read users information from table
        :param offset: Offset from where to start returning users
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: User information
        :rtype: User
        """
        stmt: Select = select(User).offset(offset).limit(limit)
        try:
            results: ScalarResult = await self.session.scalars(stmt)
            users: list[User] = results.all()
        except SQLAlchemyError as sa_exc:
            logger.error(sa_exc)
            raise DatabaseException(str(sa_exc)) from sa_exc
        return users

    @with_logging
    @benchmark
    async def create_user(
            self, user: Union[UserCreate, UserSuperCreate],
    ) -> Optional[User]:
        """
        Create user into the database
        :param user: Request object representing the user
        :type user: UserCreate or UserSuperCreate
        :return: Response object representing the created user in the
         database
        :rtype: User
        """
        hashed_password = await get_password_hash(user.password)
        user_in = user.copy(update={"password": hashed_password})
        user_create: User = User(**user_in.dict())
        try:
            self.session.add(user_create)
            await self.session.commit()
        except SQLAlchemyError as sa_exc:
            logger.error(sa_exc)
            raise DatabaseException(str(sa_exc)) from sa_exc
        try:
            created_user: User = await self.read_by_id(IdSpecification(
                user_create.id))
        except DatabaseException as db_exc:
            raise DatabaseException(str(db_exc)) from db_exc
        return created_user

    @with_logging
    @benchmark
    async def update_user(
            self, user_id: IdSpecification, user: UserUpdate
    ) -> Optional[User]:
        """
        Update user information from table
        :param user_id: Unique identifier of the user
        :type user_id: IdSpecification
        :param user: Requested user information to update
        :type user: UserUpdate
        :return: User information
        :rtype: User
        """
        try:
            found_user: User = await self.read_by_id(user_id)
        except DatabaseException as db_exc:
            raise DatabaseException(str(db_exc)) from db_exc
        user_data: dict = user.dict(exclude_unset=True)
        if user_data.get('password'):
            hashed_password = await get_password_hash(user_data["password"])
            user_data["password"] = hashed_password
        for key, value in user_data.items():
            setattr(found_user, key, value)
        user_update: UserUpdate = UserUpdate(**found_user.dict())
        async with self.session.begin():
            self.session.add(user_update)
            await self.session.commit()
        try:
            updated_user: User = await self.read_by_id(user_id)
        except DatabaseException as db_exc:
            raise DatabaseException(str(db_exc)) from db_exc
        return updated_user

    @with_logging
    @benchmark
    async def delete_user(self, user_id: IdSpecification) -> bool:
        """
        Deletes a user by its id
        :param user_id: Unique identifier of the user
        :type user_id: IdSpecification
        :return: True if the user is deleted; otherwise False
        :rtype: bool
        """
        try:
            found_user: User = await self.read_by_id(user_id)
        except DatabaseException as db_exc:
            raise DatabaseException(str(db_exc)) from db_exc
        try:
            await self.session.delete(found_user)
            await self.session.commit()
        except SQLAlchemyError as sa_exc:
            logger.error(sa_exc)
            await self.session.rollback()
            raise DatabaseException(str(sa_exc)) from sa_exc
        return True


async def get_user_repository(
        session: AsyncSession = Depends(get_session)
) -> UserRepository:
    """
    Get an instance of the user repository with the given session.
    :param session: Session object for database connectio n
    :type session: AsyncSession
    :return: UserRepository instance with session associated
    :rtype: UserRepository
    """
    return UserRepository(session, await get_index_filter(),
                          await get_unique_filter())
