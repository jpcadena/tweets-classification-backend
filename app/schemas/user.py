"""
User schema
"""
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, PositiveInt

from app.core.config import settings
from app.schemas.analysis import Analysis
from app.schemas.gender import Gender


class UserID(BaseModel):
    """
    Schema for representing a User's ID.
    """
    id: PositiveInt = Field(..., title="ID", description="ID of the User")


class UserRelationship(BaseModel):
    """
    Schema for representing the relationship between a User and
     Analyses.
    """
    analyses: Optional[list[Analysis]] = Field(
        default=[], title="Analyses", description="List of related analyses",
        unique_items=True)


class UserUpdatedAt(BaseModel):
    """
    Schema for representing the update timestamp of a User.
    """
    updated_at: Optional[datetime] = Field(
        default=None, title="Updated at",
        description="Time the User was updated")


class UserBaseAuth(BaseModel):
    """
    Schema for representing the basic authentication attributes of a
     User.
    """
    username: str = Field(
        ..., title="Username", description="Username to identify the user",
        min_length=4, max_length=15)
    email: EmailStr = Field(
        ..., title="Email", description="Preferred e-mail address of the User")


class UserFilter(UserBaseAuth, UserID):
    """
    Schema for filtering User records.
    """


class UserName(BaseModel):
    """
    Schema for representing the name attributes of a User.
    """
    first_name: str = Field(
        ..., title="First name", description="First name(s) of the User")
    last_name: str = Field(
        ..., title="Last name", description="Last name(s) of the User")


class UserBase(UserName, UserBaseAuth):
    """
    Base schema for representing a User.
    """


class UserAuth(UserBaseAuth, UserID):
    """
    User Auth that inherits from UserID.
    """

    class Config:
        """
        Config class for UserAuth
        """
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "id": 1,
                "username": "username",
                "email": "example@mail.com"}}


class UserOptional(BaseModel):
    """
    Schema for representing a User with optional attributes.
    """
    middle_name: Optional[str] = Field(
        default=None, title="Middle Name",
        description="Middle name(s) of the User")
    gender: Optional[Gender] = Field(
        default=None, title="Gender", description="Gender of the User")
    birthdate: Optional[date] = Field(
        default=None, title="Birthdate", description="Birthday of the User")
    phone_number: Optional[str] = Field(
        default=None, title="Phone number",
        description="Preferred telephone number of the User",
        regex=settings.TELEPHONE_REGEX)
    city: Optional[str] = Field(
        default="Guayaquil", title="City",
        description="City for address of the User")
    country: Optional[str] = Field(
        default="Ecuador", title="Country",
        description="Country for address of the User")


class UserCreate(UserOptional, UserBase):
    """
    Schema for creating a User record.
    """
    password: str = Field(
        ..., title="Password", description="Password of the User",
        min_length=8, max_length=14, regex=settings.PASSWORD_REGEX)

    class Config:
        """
        Config class for UserCreate
        """
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 1, 1),
                "phone_number": "+593987654321",
                "city": "Austin",
                "country": "United States"}}


class UserSuperCreate(UserCreate):
    """
    Schema for creating a superuser.
    """
    is_superuser: bool = Field(
        default=True, title="Is super user?",
        description="True if the user is super user; otherwise false")

    class Config:
        """
        Config class for UserSuperCreate
        """
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 1, 1),
                "phone_number": "+593987654321",
                "city": "Austin",
                "country": "United States",
                "is_superuser": True}}


class UserCreateResponse(UserBase, UserID):
    """
    Schema for the response when creating a User.
    """

    class Config:
        """
        Config class for UserCreateResponse
        """
        orm_mode: bool = True
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "id": 1,
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example"}}


class UserUpdate(BaseModel):
    """
    Schema for updating a User record.
    """
    username: Optional[str] = Field(
        default=None, title="Username",
        description="Username to identify the user", min_length=4,
        max_length=15)
    email: Optional[EmailStr] = Field(
        default=None, title="Email",
        description="Preferred e-mail address of the User")
    first_name: Optional[str] = Field(
        default=None, title="First name",
        description="First name(s) of the User")
    middle_name: Optional[str] = Field(
        default=None, title="Middle Name",
        description="Middle name(s) of the User")
    last_name: str = Field(
        default=None, title="Last name",
        description="Last name(s) of the User")
    password: Optional[str] = Field(
        default=None, title="New Password", min_length=8, max_length=14,
        description="New Password of the User", regex=settings.PASSWORD_REGEX)
    gender: Optional[Gender] = Field(
        default=None, title="Gender", description="Gender of the User")
    birthdate: Optional[date] = Field(
        default=None, title="Birthdate", description="Birthday of the User")
    phone_number: Optional[str] = Field(
        default=None, title="Phone number", regex=settings.TELEPHONE_REGEX,
        description="Preferred telephone number of the User")
    city: Optional[str] = Field(
        default=None, title="City", description="City for address of the User")
    country: Optional[str] = Field(
        default=None, title="Country",
        description="Country for address of the User")

    class Config:
        """
        Config class for UserUpdate
        """
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "middle_name": "One",
                "last_name": "Example",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 1, 1),
                "phone_number": "+593987654321",
                "city": "Austin",
                "country": "United States"}}


class UserInDB(UserUpdatedAt, BaseModel):
    """
    Schema for representing a User record in the database.
    """
    is_active: bool = Field(
        ..., title="Is active?",
        description="True if the user is active; otherwise false")
    is_superuser: bool = Field(
        ..., title="Is super user?",
        description="True if the user is super user; otherwise false")
    created_at: datetime = Field(
        default_factory=datetime.now, title="Created at",
        description="Time the User was created")


class UserPassword(BaseModel):
    """
    Schema for representing a User's password.
    """
    password: str = Field(
        ..., title="Hashed Password", min_length=40,
        description="Hashed Password of the User")


class UserUpdateResponse(UserInDB, UserOptional, UserPassword, UserName,
                         UserAuth):
    """
    Schema for the response when updating a User.
    """

    class Config:
        """
        Config class for UserUpdateResponse
        """
        orm_mode: bool = True
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "id": 1,
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "password": "Hk7pH9*Hk7pH9*35Fu&3UHk7pH9*35Fu&3U35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 1, 1),
                "phone_number": "+593987654321",
                "city": "Austin",
                "country": "United States",
                "is_active": True,
                "is_superuser": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()}}


class User(UserUpdatedAt, UserRelationship, UserOptional, UserBase):
    """
    Schema for representing a User.
    """
    password: str = Field(
        ..., title="Hashed Password", min_length=40,
        description="Hashed Password of the User")
    is_active: bool = Field(
        default=True, title="Is active?",
        description="True if the user is active; otherwise false")
    is_superuser: bool = Field(
        default=False, title="Is super user?",
        description="True if the user is super user; otherwise false")
    created_at: datetime = Field(
        default_factory=datetime.now, title="Created at",
        description="Time the User was created")

    class Config:
        """
        Config class for User
        """
        orm_mode: bool = True
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "id": 1,
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "password": "Hk7pH9*Hk7pH9*35Fu&3UHk7pH9*35Fu&3U35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 1, 1),
                "phone_number": "+593987654321",
                "city": "Austin",
                "country": "United States",
                "is_active": True,
                "is_superuser": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "analyses": None}}


class UserResponse(UserRelationship, UserInDB, UserOptional, UserBase, UserID):
    """
    Schema for the response when retrieving a User.
    """

    class Config:
        """
        Config class for UserResponse
        """
        orm_mode: bool = True
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "id": 1,
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "gender": Gender.MALE,
                "birthdate": date(2004, 1, 1),
                "phone_number": "+593987654321",
                "city": "Austin",
                "country": "United States",
                "is_active": True,
                "is_superuser": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "analyses": None}}
