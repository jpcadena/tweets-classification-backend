"""
User API Router
This module provides CRUD (Create, Retrieve, Update, Delete) operations
 for users.
"""
import logging
from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    HTTPException,
    Response,
    status,
)
from fastapi.params import Path, Query
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import CurrentUser
from app.core.security.exceptions import NotFoundException, ServiceException
from app.schemas.user import (
    UserCreate,
    UserCreateResponse,
    UserResponse,
    UserUpdate,
    UserUpdateResponse,
)
from app.services.user import ServiceUser
from app.utils.email_utils.email_utils import send_new_account_email

logger: logging.Logger = logging.getLogger(__name__)
# pylint: disable=unused-argument
router: APIRouter = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def get_users(
        current_user: CurrentUser, user_service: ServiceUser,
        skip: NonNegativeInt = Query(
            0, title="Skip", description="Skip users", example=0),
        limit: PositiveInt = Query(
            100, title="Limit", description="Limit pagination", example=100),
) -> list[UserResponse]:
    """
    Retrieve all users' basic information from the system using
     pagination.
    - `:param skip:` **Offset from where to start returning users**
    - `:type skip:` **NonNegativeInt**
    - `:param limit:` **Limit the number of results from query**
    - `:type limit:` **PositiveInt**
    - `:return:` **List of Users retrieved from database with id, username,
     email, first_name, last_name, middle_name, gender, birthdate,
      phone_number, city, country, is_active, is_superuser, created_at,
       updated_at and analyses relationship.**
    - `:rtype:` **list[UserResponse]**
    \f
    :param user_service: Dependency method for user service layer
    :type user_service: ServiceUser
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    try:
        found_users: list[UserResponse] = await user_service.get_users(
            skip, limit)
    except ServiceException as serv_exc:
        logger.error(serv_exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(serv_exc)
        ) from serv_exc
    return found_users


@router.post("", response_model=UserCreateResponse,
             status_code=status.HTTP_201_CREATED)
async def create_user(
        background_tasks: BackgroundTasks, user_service: ServiceUser,
        user: UserCreate = Body(
            ..., title="New user", description="New user to register")
) -> UserCreateResponse:
    """
    Register new user into the system.
    - `:param user:` **Body Object with username, email, first name,
    middle name [OPTIONAL], last name, password, gender [OPTIONAL],
    birthdate [OPTIONAL], phone_number [OPTIONAL], address [OPTIONAL],
    city [OPTIONAL], state [OPTIONAL] and country [OPTIONAL].**
    - `:type user:` **UserCreate**
    - `:return:` **User created with its id, username, email, first name
     and middle name.**
    - `:rtype:` **UserCreateResponse**
    \f
    :param background_tasks: Used for sending an email to confirm
     registration in the background
    :type background_tasks: BackgroundTasks
    :param user_service: Dependency method for user service layer
    :type user_service: ServiceUser
    """
    try:
        new_user: UserCreateResponse = await user_service.register_user(user)
    except ServiceException as serv_exc:
        detail: str = "Error at creating user."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from serv_exc
    if new_user:
        if user.email:
            background_tasks.add_task(
                send_new_account_email, user.email, user.username)
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_user_me(
        current_user: CurrentUser, user_service: ServiceUser
) -> UserResponse:
    """
    Retrieve the current user's information.
    - `:return:` **Response object for current user with id, username,
     email, first_name, last_name, middle_name, gender, birthdate,
      phone_number, city, country, is_active, is_superuser, created_at,
       updated_at and analyses relationship.**
    - `:rtype:` **UserResponse**
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    :param user_service: Dependency method for user service layer
    :type user_service: ServiceUser
    """
    try:
        user: UserResponse = await user_service.get_user_by_id(
            current_user.id)
    except ServiceException as serv_exc:
        detail: str = "Can not found user information."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail) from serv_exc
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
        user_service: ServiceUser, current_user: CurrentUser,
        user_id: PositiveInt = Path(
            ..., title="User ID", description="ID of the User to searched",
            example=1)
) -> UserResponse:
    """
    Retrieve an existing user's information given their user ID.
    - `:param user_id:` **Unique identifier of the user to be retrieved**
    - `:type user_id:` **PositiveInt**
    - `:return:` **Found user with the given ID including its username,
     email, first_name, last_name, middle_name, gender, birthdate,
      phone_number, city, country, is_active, is_superuser, created_at,
       updated_at and analyses relationship.**
    - `:rtype:` **UserResponse**
    \f
    :param user_service: Dependency method for user service layer
    :type user_service: ServiceUser
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    try:
        user: UserResponse = await user_service.get_user_by_id(user_id)
    except ServiceException as serv_exc:
        detail: str = f"User with id {user_id} not found in the system."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail) from serv_exc
    except NotFoundException as not_found_exc:
        logger.error(not_found_exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(not_found_exc)) from not_found_exc
    return user


@router.put("/{user_id}", response_model=UserUpdateResponse)
async def update_user(
        user_service: ServiceUser, current_user: CurrentUser,
        user_id: PositiveInt = Path(
            ..., title="User ID", description="ID of the User to searched",
            example=1),
        user_in: UserUpdate = Body(
            ..., title="User data", description="New user data to update")
) -> UserUpdateResponse:
    """
    Update an existing user's information given their user ID and new
     information.
    - `:param user_id:` **Unique identifier of the user to be updated**
    - `:type user_id:` **PositiveInt**
    - `:param user_in:` **New user data to update that can include:
     username, email, first_name, middle_name, last_name, password,
      gender, birthdate, phone_number, city and country.**
    - `:type user_in:` **UserUpdate**
    - `:return:` **Updated user with the given ID and its username, email,
     first_name, last_name, middle_name, hashed password, gender,
      birthdate, phone_number, city, country, is_active, is_superuser,
       created_at and updated_at.**
    - `:rtype:` **UserUpdateResponse**
    \f
    :param user_service: Dependency method for user service layer
    :type user_service: ServiceUser
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    try:
        user: UserUpdateResponse = await user_service.update_user(
            user_id, user_in)
    except ServiceException as serv_exc:
        detail: str = f"User with id {user_id} not found in the system."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from serv_exc

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_service: ServiceUser, current_user: CurrentUser,
        user_id: PositiveInt = Path(
            ..., title="User ID", description="ID of the User to searched",
            example=1)
) -> Response:
    """
    Delete an existing user given their user ID.
    - `:param user_id:` **Unique identifier of the user to be deleted**
    - `:type user_id:` **PositiveInt**
    - `:return:` **Json Response object with the deleted information**
    - `:rtype:` **Response**
    \f
    :param user_service: Dependency method for user service layer
    :type user_service: ServiceUser
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    try:
        data: dict[str, Any] = await user_service.delete_user(user_id)
    except SQLAlchemyError as sa_err:
        detail: str = "The user with this username does not exist in the system"
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from sa_err
    response: Response = Response(
        status_code=status.HTTP_204_NO_CONTENT,
        media_type="application/json")
    response.headers["deleted"] = str(data["ok"]).lower()
    response.headers["deleted_at"] = str(data["deleted_at"])
    return response
