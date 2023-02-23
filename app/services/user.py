"""
User Service to handle business logic
"""
from typing import Optional, Union
from pydantic import EmailStr, PositiveInt, NonNegativeInt, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import read_user_by_id, read_user_by_username, \
    read_user_by_email, create_user, read_users, update_user, delete_user
from app.db.base_class import Base
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.schemas.user import UserSuperCreate, UserCreateResponse, UserResponse, \
    UserUpdateResponse


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
        user: UserResponse = UserResponse.from_orm(
            await read_user_by_id(user_id, self.session))
        return user

    async def get_user_by_username(self, username: str) -> UserResponse:
        """
        Get user information with the correct schema for response
        :param username: username to retrieve User from
        :type username: str
        :return: User information
        :rtype: UserResponse
        """
        user: UserResponse = UserResponse.from_orm(
            await read_user_by_username(username, self.session))
        return user

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
        user: UserResponse = UserResponse.from_orm(db_user)
        return user

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
        user: Union[UserCreateResponse, str] = UserResponse.from_orm(
            await create_user(user, self.session))
        return user

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
            UserResponse.from_orm(user) for user in users]
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
        user: UserUpdateResponse = UserUpdateResponse.from_orm(
            await update_user(user_id, user, self.session))
        return user

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


async def model_to_schema(model: Base) -> BaseModel:
    schema: BaseModel = BaseModel.from_orm(model)
    return schema


async def user_to_response(user: User) -> UserResponse:
    user_response: UserResponse = await model_to_schema(user)
    return user_response


async def user_to_create_response(user: User) -> UserCreateResponse:
    user_response: UserCreateResponse = await model_to_schema(user)
    return user_response


async def user_to_update_response(user: User) -> UserUpdateResponse:
    user_response: UserUpdateResponse = await model_to_schema(user)
    return user_response
