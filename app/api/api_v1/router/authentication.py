"""
Login API Router
"""
from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import redis_dependency
from app.core import config
from app.core.security.exceptions import ServiceException
from app.core.security.password import verify_password
from app.crud.specification import UsernameSpecification
from app.crud.user import UserRepository, get_user_repository
from app.models.token import Token
from app.models.user import User
from app.schemas.token import TokenResponse
from app.services.auth import AuthService
from app.services.token import TokenService

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
        user: OAuth2PasswordRequestForm = Depends(),
        user_repo: UserRepository = Depends(get_user_repository),
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
    :param user_repo: Dependency method for async Postgres connection
    :type user_repo: UserRepository
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    """
    try:
        found_user: User = await user_repo.read_by_username(
            UsernameSpecification(user.username))
    except ServiceException as s_exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Invalid credentials') from s_exc
    if not await verify_password(found_user.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Incorrect password')
    if not found_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token, refresh_token, name = await AuthService.auth_token(
        found_user, setting)
    token: Token = Token(key=name, token=refresh_token)
    token_set: bool = await TokenService.create_token(token, setting, redis)
    if not token_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Could not insert data in Authorization database')
    return TokenResponse(access_token=access_token, token_type="bearer",
                         refresh_token=refresh_token)

# TODO: Create and update the reset password logic
# @router.post("/login/test-token", response_model=schemas.User)
# async def test_token(
#         current_user: models.User = Depends(get_current_user)) -> Any:
#     """
#     Test access token
#     """
#     return current_user
#
#
# @router.post("/password-recovery/{email}", response_model=schemas.Msg)
# async def recover_password(
#         email: str, user_service: AsyncSession = Depends(get_user_service)
# ) -> Any:
#     """
#     Password Recovery
#     """
#     user_service: UserService = UserService(user_service)
#     user = await user_service.read_user_by_email(email=email)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the"
#                    " system.",
#         )
#     password_reset_token = generate_password_reset_token(email=email)
#     send_reset_password_email(
#         email_to=user.email, email=email, token=password_reset_token
#     )
#     return {"msg": "Password recovery email sent"}
#
#
# @router.post("/reset-password/", response_model=schemas.Msg)
# async def reset_password(
#         token: str = Body(...),
#         new_password: str = Body(...),
#         user_service: AsyncSession = Depends(get_user_service),
# ) -> Any:
#     """
#     Reset password
#     """
#     email = verify_password_reset_token(token)
#     if not email:
#         raise HTTPException(status_code=400, detail="Invalid token")
#     user_service: UserService = UserService(user_service)
#     user = user_service.read_user_by_email(email)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the"
#                    " system.",
#         )
#     # elif not crud.user.is_active(user):
#     #     raise HTTPException(status_code=400, detail="Inactive user")
#     hashed_password = await get_password_hash(new_password)
#     user.hashed_password = hashed_password
#     user_service.add(user)
#     await user_service.commit()
#     return {"msg": "Password updated successfully"}
