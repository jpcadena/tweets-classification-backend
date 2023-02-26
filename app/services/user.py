"""
User Service to handle business logic
"""
from typing import Optional, Union, TypeVar

from pydantic import EmailStr, PositiveInt, NonNegativeInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import read_user_by_id, read_user_by_username, \
    read_user_by_email, create_user, read_users, update_user, delete_user
from app.models import User
from app.schemas.user import UserSuperCreate, UserCreateResponse, UserResponse, \
    UserUpdateResponse, UserCreate, UserUpdate

T = TypeVar('T', UserResponse, UserCreateResponse, UserUpdateResponse)


async def model_to_response(model: User, response_model: T) -> T:
    """
    Converts a User object to a Pydantic response model
    :param model: Object from Pydantic Base Model class
    :type model: User
    :param response_model: Response model
    :type response_model: T
    :return: Model inherited from SQLAlchemy Declarative Base
    :rtype: T
    """
    return response_model.from_orm(model)


class UserService:
    """
    User service class
    """

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """
        Get user information with the correct schema for response
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: User information
        :rtype: UserResponse
        """
        user: User = await read_user_by_id(user_id, self.session)
        return await model_to_response(user, UserResponse)

    async def get_user_by_username(self, username: str) -> UserResponse:
        """
        Get user information with the correct schema for response
        :param username: username to retrieve User from
        :type username: str
        :return: User information
        :rtype: UserResponse
        """
        user: User = await read_user_by_username(username, self.session)
        return await model_to_response(user, UserResponse)

    async def get_user_by_email(
            self, email: EmailStr) -> Optional[UserResponse]:
        """
        Read the user from the database with unique email
        :param self.session: Async Session for Database
        :type self.session: AsyncSession
        :param email: Email to retrieve User from
        :type email: EmailStr
        :return: User found in database
        :rtype: UserResponse
        """
        db_user: User = await read_user_by_email(email, self.session)
        if not db_user:
            return None
        return await model_to_response(db_user, UserResponse)

    async def create_user(
            self, user: Union[UserCreate, UserSuperCreate]
    ) -> Union[UserCreateResponse, str]:
        """
        Create user into the database
        :param user: Request object representing the user
        :type user: UserCreate or UserSuperCreate
        :return: Response object representing the created user in the
         database
        :rtype: UserCreateResponse or exception
        """
        created_user = await create_user(user, self.session)
        if isinstance(created_user, str):
            return created_user
        return await model_to_response(created_user, UserCreateResponse)

    async def get_users(
            self, offset: NonNegativeInt, limit: PositiveInt
    ) -> Optional[list[UserResponse]]:
        """
        Read users information from table
        :param self.session: Async Session for Database
        :type self.session: AsyncSession
        :param offset: Offset from where to start returning users
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: User information
        :rtype: UserResponse
        """
        users: list[User] = await read_users(offset, limit, self.session)
        found_users: list[UserResponse] = [
            await model_to_response(user, UserResponse) for user in users]
        return found_users

    async def update_user(
            self, user_id: int, user: UserUpdate
    ) -> Optional[UserUpdateResponse]:
        """
        Update user information from table
        :param user_id: Unique identifier of the user
        :type user_id: int
        :param user: Requested user information to update
        :type user: UserUpdate
        :param self.session: Async Session for Database
        :type self.session: AsyncSession
        :return: User information
        :rtype: UserUpdateResponse
        """
        updated_user: User = await update_user(user_id, user, self.session)
        return await model_to_response(updated_user, UserUpdateResponse)

    async def delete_user(self, user_id: int) -> bool:
        """
        Deletes a user by its id
        :param user_id: Unique identifier of the user
        :type user_id: int
        :return: True if the user is deleted; otherwise False
        :rtype: bool
        """
        deleted: bool = await delete_user(user_id, self.session)
        return deleted
