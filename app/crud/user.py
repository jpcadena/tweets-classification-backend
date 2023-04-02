"""
User CRUD script
"""
import logging
from datetime import datetime
from typing import Optional, Union

from fastapi.encoders import jsonable_encoder
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import ScalarResult, Select, select, Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def read_by_id(self, _id: IdSpecification) -> Optional[User]:
        """
        Reads the user by its id
        :param _id:
        :type _id: IdSpecification
        :return: User instance
        :rtype: User
        """
        async with self.session as session:
            try:
                user: User = await self.index_filter.filter(
                    _id, session, self.model)
            except SQLAlchemyError as db_exc:
                raise DatabaseException(str(db_exc)) from db_exc
            return user

    async def read_by_username(
            self, username: UsernameSpecification) -> User:
        """
        Read the user by its username
        :param username: The username to search
        :type username: UsernameSpecification
        :return: User instance
        :rtype: User
        """
        async with self.session as session:
            try:
                user: User = await self.unique_filter.filter(
                    username, session, self.model, "username")
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
        async with self.session as session:
            try:
                user: User = await self.unique_filter.filter(
                    email, session, self.model, "email")
            except SQLAlchemyError as db_exc:
                raise DatabaseException(str(db_exc)) from db_exc
            return user

    async def read_id_by_email(
            self, email: EmailSpecification) -> Optional[PositiveInt]:
        """
        Read the user by its email
        :param email: The email to search
        :type email: EmailSpecification
        :return: User instance
        :rtype: PositiveInt
        """
        async with self.session as session:
            try:
                stmt: Select = select(User.id).where(
                    self.model.email == email.value)
                result: Result = await session.execute(stmt)
                user_id: PositiveInt = result.scalar()
            except SQLAlchemyError as db_exc:
                raise DatabaseException(str(db_exc)) from db_exc
            return user_id

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
        async with self.session as session:
            try:
                results: ScalarResult = await session.scalars(stmt)
                users: list[User] = results.all()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(str(sa_exc)) from sa_exc
            return users

    @with_logging
    @benchmark
    async def create_user(
            self, user: Union[UserCreate, UserSuperCreate],
    ) -> User:
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
        async with self.session as session:
            try:
                session.add(user_create)
                await session.commit()
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
        async with self.session as session:
            try:
                found_user: User = await self.read_by_id(user_id)
            except DatabaseException as db_exc:
                raise DatabaseException(str(db_exc)) from db_exc
            obj_data: dict = jsonable_encoder(found_user)
            update_data: dict = user.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    if field == "password":
                        setattr(found_user, field, await get_password_hash(
                            update_data[field]))
                    else:
                        setattr(found_user, field, update_data[field])
                if field == "updated_at":
                    setattr(found_user, field, datetime.utcnow())
            session.add(found_user)
            await session.commit()
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
        async with self.session as session:
            try:
                found_user: User = await self.read_by_id(user_id)
            except DatabaseException as db_exc:
                raise DatabaseException(str(db_exc)) from db_exc
            try:
                await session.delete(found_user)
                await session.commit()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                await session.rollback()
                raise DatabaseException(str(sa_exc)) from sa_exc
            return True


async def get_user_repository() -> UserRepository:
    """
    Get an instance of the user repository with the given session.
    :return: UserRepository instance with session associated
    :rtype: UserRepository
    """
    return UserRepository(await get_session(), await get_index_filter(),
                          await get_unique_filter())
