"""
Token schema
"""
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr, AnyUrl

from app.core import config
from app.core.config import settings
from app.schemas.scope import Scope


class PublicClaimsToken(BaseModel):
    """
    Token class based on Pydantic Base Model with Public claims (IANA).
    """
    email: EmailStr = Field(
        ..., title="Email", description="Preferred e-mail address of the User",
        unique=True)
    nickname: str = Field(
        title="Casual name",
        description="Casual name of the User (First Name)", min_length=1,
        max_length=50)
    preferred_username: str = Field(
        ..., title="Preferred username",
        description="Shorthand name by which the End-User wishes to be "
                    "referred to (Username)", min_length=1, max_length=50,
        unique=True)


class RegisteredClaimsToken(BaseModel):
    """
    Registered Claims Token class based on Pydantic Base Model with
    Registered claims.
    """
    iss: AnyUrl = Field(
        default=config.get_settings().SERVER_HOST, title="Issuer",
        description="Principal that issued JWT as HTTP URL")
    sub: str = Field(
        ..., title="Subject",
        description="Subject of JWT starting with username: followed"
                    " by User ID", min_length=1, regex=settings.SUB_REGEX)
    aud: str = Field(
        default=settings.AUDIENCE,
        title="Audience", description="Recipient of JWT", const=True,
        min_length=1)
    exp: int = Field(
        ..., title="Expiration time",
        description="Expiration time on or after which the JWT MUST NOT be"
                    " accepted for processing", gt=1)
    nbf: int = Field(
        ..., title="Not Before",
        description="Time Before which the JWT MUST NOT be accepted for "
                    "processing", gt=1)
    iat: int = Field(
        ..., title="Issued At", description="Time at which the JWT was issued",
        gt=1)
    jti: UUID = Field(
        default_factory=uuid4, title="JWT ID",
        description="Unique Identifier for the JWT", unique=True)
    scope: Scope = Field(
        default=Scope.ACCESS_TOKEN, title="Scope", description="Scope value")


class TokenPayload(PublicClaimsToken, RegisteredClaimsToken):
    """
    Token Payload class based on RegisteredClaimsToken and PublicClaimsToken.
    """

    @classmethod
    def get_field_names(cls, alias: bool = False) -> list:
        """
        Retrieve the class attributes as a list.
        :param alias: Check for alias in the schema
        :type alias: bool
        :return: class attributes
        :rtype: list
        """
        return list(cls.schema(alias).get("properties").keys())

    class Config:
        """
        Config class for Token Payload
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "iss": "http://localhost:8000",
                "sub": "username:63aefa38afda3a176c1e3562",
                "aud": "http://localhost:8000/authentication/login",
                "exp": 1672433102, "nbf": 1672413301, "iat": 1672413302,
                "jti": "ce0f27c1-c559-45b1-b016-a81a600af197",
                "scope": "access_token", "nickname": "Juan",
                "preferred_username": "jpcadena",
                "email": "jpcadena@espol.edu.ec"}}


class TokenResponse(BaseModel):
    """
    Token for Response based on Pydantic Base Model.
    """
    access_token: str = Field(..., title="Token", description="Access token")
    token_type: str = Field(
        ..., title="Token type", description="Type of the token")
    refresh_token: str = Field(
        ..., title="Refresh Token", description="Refresh token")

    class Config:
        """
        Config class for TokenResponse
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "token_type": "bearer",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}}


class TokenResetPassword(BaseModel):
    """
    Token Reset Password for Request based on Pydantic Base Model.
    """
    token: str = Field(
        ..., title="Token", description="Access token", min_length=30)
    password: str = Field(
        ..., title="New password", description="New password to reset",
        min_length=8, max_length=14, regex=settings.PASSWORD_REGEX)

    class Config:
        """
        Config class for Token Reset Password
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "password": "Hk7pH9*35Fu&3U"}}
