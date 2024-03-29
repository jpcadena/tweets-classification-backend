"""
User Service to handle business logic
"""
import logging
from datetime import datetime
from typing import Annotated, Any, Optional, Type, Union

from fastapi import Depends
from pydantic import EmailStr, NonNegativeInt, PositiveInt

from app.core.security.exceptions import (
    DatabaseException,
    NotFoundException,
    ServiceException,
)
from app.crud.specification import (
    EmailSpecification,
    IdSpecification,
    UsernameSpecification,
)
from app.crud.user import UserRepository, get_user_repository
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserCreateResponse,
    UserResponse,
    UserSuperCreate,
    UserUpdate,
    UserUpdateResponse,
)
from app.services import model_to_response

logger: logging.Logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user-related business logic.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo: UserRepository = user_repo

    async def get_user_by_id(
            self, user_id: PositiveInt
    ) -> Optional[UserResponse]:
        """
        Retrieve user information by its unique identifier
        :param user_id: Unique identifier of the user
        :type user_id: PositiveInt
        :return: User information
        :rtype: Optional[UserResponse]
        """
        try:
            user: User = await self.user_repo.read_by_id(
                IdSpecification(user_id))
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        if not user:
            detail: str = f"User with id {user_id} not found in the system."
            logger.error(detail)
            raise NotFoundException(detail)
        user_response: UserResponse = await model_to_response(
            user, UserResponse)
        return user_response

    async def get_login_user(self, username: str) -> User:
        """
        Retrieve user information for login purposes by its username
        :param username: The username to retrieve User from
        :type username: str
        :return: User information
        :rtype: User
        """
        try:
            user: User = await self.user_repo.read_by_username(
                UsernameSpecification(username))
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        return user

    async def get_user_by_username(self, username: str) -> UserResponse:
        """
        Retrieve user information by its username
        :param username: The username to retrieve User from
        :type username: str
        :return: User information
        :rtype: UserResponse
        """
        try:
            user: User = await self.get_login_user(username)
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(user, UserResponse)

    async def get_user_by_email(
            self, email: EmailStr
    ) -> Optional[UserResponse]:
        """
        Retrieve user information by its unique email.
        :param email: The email to retrieve User from
        :type email: EmailStr
        :return: User found in database
        :rtype: Optional[UserResponse]
        """
        try:
            user: User = await self.user_repo.read_by_email(
                EmailSpecification(email))
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(user, UserResponse)

    async def get_user_id_by_email(
            self, email: EmailStr
    ) -> Optional[PositiveInt]:
        """
        Read the user ID from the database with unique email.
        :param email: Email to retrieve User from
        :type email: EmailStr
        :return: User ID found in database
        :rtype: PositiveInt
        """
        try:
            user_id: PositiveInt = await self.user_repo.read_id_by_email(
                EmailSpecification(email))
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        return user_id

    async def register_user(
            self, user: Union[UserCreate, UserSuperCreate]
    ) -> UserCreateResponse:
        """
        Register a new user in the database
        :param user: Request object representing the user
        :type user: Union[UserCreate, UserSuperCreate]
        :return: Response object representing the created user in the
         database
        :rtype: UserCreateResponse
        """
        try:
            created_user = await self.user_repo.create_user(user)
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(created_user, UserCreateResponse)

    async def get_users(
            self, offset: NonNegativeInt, limit: PositiveInt
    ) -> list[UserResponse]:
        """
        Retrieve users' information from the table
        :param offset: Offset from where to start returning users
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: User information
        :rtype: list[UserResponse]
        """
        try:
            users: list[User] = await self.user_repo.read_users(offset, limit)
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        found_users: list[UserResponse] = [
            await model_to_response(user, UserResponse) for user in users]
        return found_users

    async def update_user(
            self, user_id: PositiveInt, user: UserUpdate
    ) -> Optional[UserUpdateResponse]:
        """
        Update user information from table
        :param user_id: Unique identifier of the user
        :type user_id: PositiveInt
        :param user: Requested user information to update
        :type user: UserUpdate
        :return: User information
        :rtype: Optional[UserUpdateResponse]
        """
        try:
            updated_user: User = await self.user_repo.update_user(
                IdSpecification(user_id), user)
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(updated_user, UserUpdateResponse)

    async def delete_user(self, user_id: PositiveInt) -> dict[str, Any]:
        """
        Deletes a user by its id
        :param user_id: Unique identifier of the user
        :type user_id: PositiveInt
        :return: Data to confirmation info about the delete process
        :rtype: dict[str, Any]
        """
        try:
            deleted: bool = await self.user_repo.delete_user(
                IdSpecification(user_id))
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        return {"ok": deleted, "deleted_at": datetime.now()}


async def get_user_service(
        user_repo: UserRepository = Depends(
            get_user_repository)
) -> UserService:
    """
    Get an instance of the user service with the given repository.
    :param user_repo: User repository object for database connection
    :type user_repo: UserRepository
    :return: UserService instance with repository associated
    :rtype: UserService
    """
    return UserService(user_repo)


ServiceUser: Type[UserService] = Annotated[
    UserService, Depends(get_user_service)]
