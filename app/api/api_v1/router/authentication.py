"""
Authentication API Router.
This module provides login and password recovery functionality.
"""
import logging
from typing import Annotated

from aioredis import Redis
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, PositiveInt

from app.api.deps import CurrentUser, redis_dependency
from app.core import config
from app.core.security.exceptions import ServiceException
from app.core.security.password import verify_password
from app.models.token import Token
from app.models.user import User
from app.schemas.msg import Msg
from app.schemas.token import TokenResetPassword, TokenResponse
from app.schemas.user import (
    UserAuth,
    UserResponse,
    UserUpdate,
    UserUpdateResponse,
)
from app.services.auth import AuthService
from app.services.token import TokenService
from app.services.user import ServiceUser
from app.utils.email_utils.email_utils import send_reset_password_email
from app.utils.security.password import (
    generate_password_reset_token,
    verify_password_reset_token,
)

logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
        user_service: ServiceUser,
        settings: Annotated[config.Settings, Depends(config.get_settings)],
        user: OAuth2PasswordRequestForm = Depends(),
        redis: Redis = Depends(redis_dependency)
) -> TokenResponse:
    """
    Endpoint to handle user login with OAuth2 authentication using
     request form.
    ## Parameter:
    - `user:` **Request body with username and password**
    - `type:` **OAuth2PasswordRequestForm**
    ## Response:
    - `return:` **Token information with access token, its type and
     refresh token**
    - `rtype:` **TokenResponse**
    \f
    :param user_service: Dependency method for User Service
    :type user_service: ServiceUser
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    """
    try:
        found_user: User = await user_service.get_login_user(user.username)
    except ServiceException as s_exc:
        logger.error(s_exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid credentials") from s_exc
    if not await verify_password(found_user.password, user.password):
        detail: str = "Incorrect password"
        logger.warning(detail)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)
    if not found_user.is_active:
        user_detail: str = "Inactive user"
        logger.warning(user_detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=user_detail)
    access_token, refresh_token, name = await AuthService.auth_token(
        found_user, settings)
    token: Token = Token(key=name, token=refresh_token)
    token_set: bool = await TokenService.create_token(token, settings, redis)
    if not token_set:
        data_detail: str = "Could not insert data in Authentication database"
        logger.warning(data_detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=data_detail)
    return TokenResponse(access_token=access_token, token_type="bearer",
                         refresh_token=refresh_token)


@router.post("/login/test-token", response_model=UserAuth)
async def test_token(
        current_user: CurrentUser) -> UserAuth:
    """
    Endpoint to test the validity of an access token.
    ## Response:
    - `return:` **The authenticated user instance**
    - `rtype:` **UserAuth**
    \f
    :param current_user: The current user
    :type current_user: CurrentUser
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=Msg)
async def recover_password(
        user_service: ServiceUser,
        settings: Annotated[config.Settings, Depends(config.get_settings)],
        email: EmailStr = Path(
            ..., title="Email",
            description="The email used to recover the password",
            example="someone@example.com")
) -> Msg:
    """
    Endpoint to handle password recovery.
    ## Parameter:
    - `email:` **Path parameter that references the email used to recover
     the password**
    - `type:` **EmailStr**
    ## Response:
    - `return:` **Message object**
    - `rtype:` **Msg**
    \f
    :param user_service: Dependency method for User service object
    :type user_service: ServiceUser
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    """
    try:
        user: UserResponse = await user_service.get_user_by_email(email)
    except ServiceException as s_exc:
        logger.error(s_exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There was an issue with the request") from s_exc
    if not user:
        detail: str = "The user with this username does not exist in the" \
                      " system."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    password_reset_token: str = await generate_password_reset_token(
        email, settings)
    await send_reset_password_email(
        user.email, user.username, password_reset_token, settings)
    return Msg(msg="Password recovery email sent")


@router.post("/reset-password/", response_model=Msg)
async def reset_password(
        user_service: ServiceUser,
        token_reset_password: TokenResetPassword = Body(
            ..., title="Body object",
            description="Object with access token and new password")
) -> Msg:
    """
    Endpoint to handle password reset.
    ## Parameter:
    - `token_reset_password:` **Body Object with token and new password**
    - `type:` **TokenResetPassword**
    ## Response:
    - `return:` **Message object**
    - `rtype:` **Msg**
    \f
    :param user_service: Dependency method for User service object
    :type user_service: ServiceUser
    """
    email: EmailStr = await verify_password_reset_token(
        token_reset_password.token)
    if not email:
        invalid_token: str = "Invalid token"
        logger.error(invalid_token)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=invalid_token)
    try:
        user_id: PositiveInt = await user_service.get_user_id_by_email(email)
    except ServiceException as s_exc:
        logger.error(s_exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There was an issue with the request") from s_exc
    if not user_id:
        detail: str = f"The user with this email {email} does not exist in" \
                      f" the system."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail)
    user_update: UserUpdate = UserUpdate(**{
        "password": token_reset_password.password})
    user: UserUpdateResponse = await user_service.update_user(
        user_id, user_update)
    return Msg(msg=f"Password updated successfully for {user.email}")
