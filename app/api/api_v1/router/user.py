"""
User API Router
"""
import re
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, \
    status
from fastapi.params import Query, Path
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core import config
from app.db.session import database_session
from app.schemas.user import UserResponse, UserCreateResponse, UserCreate, \
    UserAuth, UserUpdate, UserUpdateResponse
from app.services.user import UserService
from app.utils import send_new_account_email

router: APIRouter = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def get_users(
        skip: NonNegativeInt = Query(
            0, title='Skip', description='Skip users', example=0),
        limit: PositiveInt = Query(
            100, title='Limit', description='Limit pagination', example=100),
        session: AsyncSession = Depends(database_session),
        current_user: UserAuth = Depends(get_current_user),
) -> list[UserResponse]:
    """
    Get all Users basic information from the system.
    - :return: List of Users retrieved from database with username and email
    - :rtype: list[UserDisplay]
    \f
    :param session: Dependency method for async Postgres connection
    :type session: AsyncSession
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    user_service: UserService = UserService(session)
    found_users: list[UserResponse] = await user_service.get_users(
        skip, limit)
    if not found_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Users not found in the system.')
    return found_users


@router.post('', response_model=UserCreateResponse,
             status_code=status.HTTP_201_CREATED)
async def register_user(
        background_tasks: BackgroundTasks,
        user: UserCreate = Body(..., title='New user',
                                description='New user to register'),
        session: AsyncSession = Depends(database_session),
        setting: config.Settings = Depends(config.get_setting)
) -> UserCreateResponse:
    """
    Register new user into the system.
    - :param user: Body Object with username, email, first name,
    middle name [OPTIONAL], last name, password, gender [OPTIONAL],
    birthdate [OPTIONAL], phone_number [OPTIONAL], address [OPTIONAL],
    city [OPTIONAL], state [OPTIONAL] and country [OPTIONAL].
    - :type user: UserCreate
    - :return: User created with its name and email
    - :rtype: UserDisplay
    \f
    :param background_tasks: Send email to confirm registration
    :type background_tasks: BackgroundTasks
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    """
    user_service: UserService = UserService(session)
    new_user = await user_service.create_user(user)
    if isinstance(new_user, str):
        if "duplicate key value violates unique constraint" in new_user:
            match = re.search(r'Key \((\w+)\)=\((.*)\)', new_user)
            if match:
                field: str = match.group(1)
                value: str = match.group(2)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'User with {field}: {value} already exists in the'
                           f' system.')
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail=f'User with invalid data: {new_user}')
    if new_user:
        if setting.EMAILS_ENABLED and user.email:
            background_tasks.add_task(send_new_account_email, user.email,
                                      user.username, setting)
    return new_user


# @router.put("/me", response_model=schemas.User)
# def update_user_me(
#         *,
#         session: AsyncSession = Depends(deps.get_session),
#         password: str = Body(None),
#         full_name: str = Body(None),
#         email: EmailStr = Body(None),
#         current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Update own user.
#     """
#     current_user_data = jsonable_encoder(current_user)
#     user_in = schemas.UserUpdate(**current_user_data)
#     if password is not None:
#         user_in.password = password
#     if full_name is not None:
#         user_in.full_name = full_name
#     if email is not None:
#         user_in.email = email
#     user = UserService.update(session, session_obj=current_user, obj_in=user_in)
#     return user


@router.get("/me", response_model=UserResponse)
async def get_user_me(
        session: AsyncSession = Depends(database_session),
        current_user: UserAuth = Depends(get_current_user),
) -> UserResponse:
    """
    Get current user.
    """
    user_service: UserService = UserService(session)
    user: UserResponse = await user_service.get_user_by_id(current_user.id)
    return user


@router.get("/user_id", response_model=UserResponse)
async def get_user_by_id(
        user_id: int = Path(...),
        session: AsyncSession = Depends(database_session),
        current_user: UserAuth = Depends(get_current_user),
) -> UserResponse:
    """
    Get
    :param user_id:
    :type user_id:
    :return:
    :rtype:
    \f
    :param session: Dependency method for async Postgres connection
    :type session: AsyncSession
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    user_service: UserService = UserService(session)
    user: UserResponse = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {user_id} not found in the system.')
    return user


@router.put("/{user_id}", response_model=UserUpdateResponse)
async def update_user(
        user_id: int = Path(...),
        user_in: UserUpdate = Body(...),
        session: AsyncSession = Depends(database_session),
        current_user: UserAuth = Depends(get_current_user),
) -> UserUpdateResponse:
    """
    Update a user.
    """
    user_service: UserService = UserService(session)
    user: UserUpdateResponse = await user_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    return user
