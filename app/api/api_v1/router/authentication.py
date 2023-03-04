"""
Login API Router
"""
import logging

from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, PositiveInt

from app.api.deps import redis_dependency, get_current_user
from app.core import config
from app.core.security.exceptions import ServiceException
from app.core.security.password import verify_password
from app.models.token import Token
from app.models.user import User
from app.schemas.msg import Msg
from app.schemas.token import TokenResponse, TokenResetPassword
from app.schemas.user import UserAuth, UserResponse, UserUpdate, \
    UserUpdateResponse
from app.services.auth import AuthService
from app.services.token import TokenService
from app.services.user import get_user_service, UserService
from app.utils.utils import generate_password_reset_token, \
    send_reset_password_email, verify_password_reset_token

logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
        user: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(get_user_service),
        setting: config.Settings = Depends(config.get_setting),
        redis: Redis = Depends(redis_dependency)
) -> TokenResponse:
    """
    Login with OAuth2 authentication using request form.
    - :param user: Object from request body with username and password
     as DI
    - :type user: OAuth2PasswordRequestForm
    - :return: Token information with access token, its type and
     refresh token
    - :rtype: TokenResponse
    \f
    :param user_service: Dependency method for User Service
    :type user_service: UserService
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    """
    try:
        found_user: User = await user_service.get_login_user(user.username)
    except ServiceException as s_exc:
        logger.error(s_exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Invalid credentials') from s_exc
    if not await verify_password(found_user.password, user.password):
        logger.warning('Incorrect password')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Incorrect password')
    if not found_user.is_active:
        logger.warning('Inactive user')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Inactive user')
    access_token, refresh_token, name = await AuthService.auth_token(
        found_user, setting)
    token: Token = Token(key=name, token=refresh_token)
    token_set: bool = await TokenService.create_token(token, setting, redis)
    if not token_set:
        logger.warning('Could not insert data in Authorization database')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Could not insert data in Authorization database')
    return TokenResponse(access_token=access_token, token_type="bearer",
                         refresh_token=refresh_token)


@router.post("/login/test-token", response_model=UserAuth)
async def test_token(
        current_user: UserAuth = Depends(get_current_user)) -> UserAuth:
    """
    Test access token
    :param current_user: The current user
    :type current_user: UserAuth
    :return: User instance
    :rtype: UserAuth
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=Msg)
async def recover_password(
        email: EmailStr, user_service: UserService = Depends(get_user_service)
) -> Msg:
    """
    Recover password
    - :param email: The email to recover
    - :type email: EmailStr
    - :return: Message object
    - :rtype: Msg
    \f
    :param user_service: Dependency method for User service object
    :type user_service: UserService
    """
    try:
        user: UserResponse = await user_service.get_user_by_email(email)
    except ServiceException as s_exc:
        logger.error(s_exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='There was an issue with the request') from s_exc
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system.")
    password_reset_token: str = await generate_password_reset_token(email)
    await send_reset_password_email(
        user.email, user.username, password_reset_token)
    return Msg(msg="Password recovery email sent")


@router.post("/reset-password/", response_model=Msg)
async def reset_password(
        token_reset_password: TokenResetPassword = Body(
            ..., title='Body object',
            description='Object with access token and new password'),
        user_service: UserService = Depends(get_user_service),
) -> Msg:
    """
    Reset password
    - :param token_reset_password: Object with token and new password
    - :type token_reset_password: TokenResetPassword
    - :return: Message object
    - :rtype: Msg
    \f

    :param user_service:
    :type user_service:
    """
    email: EmailStr = await verify_password_reset_token(
        token_reset_password.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    try:
        user_id: PositiveInt = await user_service.get_user_id_by_email(email)
    except ServiceException as s_exc:
        logger.error(s_exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='There was an issue with the request') from s_exc
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user with this email {email} does not exist in the"
                   f" system.")
    user_update: UserUpdate = UserUpdate(**{
        "password": token_reset_password.password})
    user: UserUpdateResponse = await user_service.update_user(
        user_id, user_update)
    return Msg(msg=f"Password updated successfully for {user.email}")
