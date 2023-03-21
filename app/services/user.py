"""
User Service to handle business logic
"""
from datetime import datetime
from typing import Optional, Union, Type, Annotated

from fastapi import Depends
from pydantic import EmailStr, PositiveInt, NonNegativeInt

from app.core.security.exceptions import DatabaseException, ServiceException, \
    NotFoundException
from app.crud.specification import IdSpecification, UsernameSpecification, \
    EmailSpecification
from app.crud.user import UserRepository, get_user_repository
from app.models.user import User
from app.schemas.user import UserSuperCreate, UserCreateResponse, \
    UserResponse, UserUpdateResponse, UserCreate, UserUpdate
from app.services import model_to_response


class UserService:
    """
    User service class
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo: UserRepository = user_repo

    async def get_user_by_id(
            self, user_id: PositiveInt) -> Optional[UserResponse]:
        """
        Get user information with the correct schema for response
        :param user_id: Unique identifier of the user
        :type user_id: PositiveInt
        :return: User information
        :rtype: UserResponse
        """
        try:
            user: User = await self.user_repo.read_by_id(
                IdSpecification(user_id))
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        if not user:
            raise NotFoundException(
                f"User with id {user_id} not found in the system.")
        user_response: UserResponse = await model_to_response(
            user, UserResponse)
        return user_response

    async def get_login_user(self, username: str) -> User:
        """
        Get user information with the correct schema for response
        :param username: username to retrieve User from
        :type username: str
        :return: User information
        :rtype: UserResponse
        """
        try:
            user: User = await self.user_repo.read_by_username(
                UsernameSpecification(username))
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return user

    async def get_user_by_username(self, username: str) -> UserResponse:
        """
        Get user information with the correct schema for response
        :param username: username to retrieve User from
        :type username: str
        :return: User information
        :rtype: UserResponse
        """
        try:
            user: User = await self.get_login_user(username)
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(user, UserResponse)

    async def get_user_by_email(
            self, email: EmailStr) -> Optional[UserResponse]:
        """
        Read the user from the database with unique email.
        :param email: Email to retrieve User from
        :type email: EmailStr
        :return: User found in database
        :rtype: UserResponse
        """
        try:
            user: User = await self.user_repo.read_by_email(
                EmailSpecification(email))
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(user, UserResponse)

    async def get_user_id_by_email(
            self, email: EmailStr) -> Optional[PositiveInt]:
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
            raise ServiceException(str(db_exc)) from db_exc
        return user_id

    async def register_user(
            self, user: Union[UserCreate, UserSuperCreate]
    ) -> UserCreateResponse:
        """
        Create user into the database
        :param user: Request object representing the user
        :type user: UserCreate or UserSuperCreate
        :return: Response object representing the created user in the
         database
        :rtype: UserCreateResponse or exception
        """
        try:
            created_user = await self.user_repo.create_user(user)
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(created_user, UserCreateResponse)

    async def get_users(
            self, offset: NonNegativeInt, limit: PositiveInt
    ) -> list[UserResponse]:
        """
        Read users information from table
        :param offset: Offset from where to start returning users
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: User information
        :rtype: UserResponse
        """
        try:
            users: list[User] = await self.user_repo.read_users(offset, limit)
        except DatabaseException as db_exc:
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
        :rtype: UserUpdateResponse
        """
        try:
            updated_user: User = await self.user_repo.update_user(
                IdSpecification(user_id), user)
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(updated_user, UserUpdateResponse)

    async def delete_user(self, user_id: PositiveInt) -> dict:
        """
        Deletes a user by its id
        :param user_id: Unique identifier of the user
        :type user_id: PositiveInt
        :return: Data to confirmation info about the delete process
        :rtype: dict
        """
        try:
            deleted: bool = await self.user_repo.delete_user(
                IdSpecification(user_id))
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return {"ok": deleted, 'deleted_at': datetime.now()}


async def get_user_service(
        user_repo: UserRepository = Depends(
            get_user_repository)) -> UserService:
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
