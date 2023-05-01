"""
Core config script
"""
import base64
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, \
    validator, RedisDsn, root_validator


def get_image_b64(image_path: str) -> str:
    """
    Get the image in 64-bytes format
    :param image_path: The path to the image
    :type image_path: str
    :return: The image in 64-bytes format
    :rtype: str
    """
    return base64.b64encode(Path(image_path).read_bytes()).decode("utf")


img_b64: str = get_image_b64("./app/assets/images/api-docs.png")
users_b64: str = get_image_b64("./app/assets/images/users.png")
analyses_b64: str = get_image_b64("./app/assets/images/analyses.png")
models_b64: str = get_image_b64("./app/assets/images/models.png")
auth_b64: str = get_image_b64("./app/assets/images/auth.png")


class Settings(BaseSettings):
    """
    Settings class based on Pydantic Base Settings
    """
    SECRET_KEY: str
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    PROJECT_NAME: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    VERSION: str
    ENCODING: str
    DATE_FORMAT: str
    FILE_DATE_FORMAT: str
    LOG_FORMAT: str
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    API_V1_STR: str
    OPENAPI_FILE_PATH: str
    TOKEN_URL: str
    STOP_WORDS_FILE_PATH: str
    IMAGES_PATH: str
    IMAGES_DIRECTORY: str
    EMAIL_TEMPLATES_DIR: str

    AUDIENCE: Optional[str] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
            cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        """
        Assemble Backend CORS origins validator.
        :param v:
        :type v: Union[str, list[str]]
        :return: List of Backend CORS origins to be accepted
        :rtype: Union[list[str], str]
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("AUDIENCE", pre=True)
    def assemble_audience(
            cls, v: Optional[str], values: dict[str, Any]) -> str:
        """
        Combine server host and API_V1_STR to create the audience string.
        :param v: The value of audience attribute
        :type v: Optional[str]
        :param values: The values to assemble the audience string
        :type values: dict[str, Any]
        :return: The AUDIENCE attribute
        :rtype: str
        """
        return f"{values['SERVER_HOST']}{values['API_V1_STR']}/auth/login"

    TELEPHONE_REGEX: str
    PASSWORD_REGEX: str
    SUB_REGEX: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    TS_PRECISION: int
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
            cls, v: Optional[str], values: dict[str, Any]) -> Any:
        """
        Assemble the database connection as URI string
        :param v: Variables to consider
        :type v: str
        :param values: Variables names and its values
        :type values: dict[str, Any]
        :return: SQLAlchemy URI
        :rtype: PostgresDsn
        """
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    DB_EMAIL_CONSTRAINT: str
    DB_TELEPHONE_CONSTRAINT: str
    DB_TW_USERNAME_CONSTRAINT: str

    SMTP_TLS: bool
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    MAIL_SUBJECT: str
    MAIL_TIMEOUT: float

    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int
    EMAILS_ENABLED: bool

    SUPERUSER_EMAIL: EmailStr
    SUPERUSER_FIRST_NAME: str
    SUPERUSER_PASSWORD: str

    REDIS_HOST: str
    REDIS_USERNAME: str
    REDIS_PASSWORD: str
    REDIS_PORT: int
    AIOREDIS_DATABASE_URI: Optional[RedisDsn] = None

    @validator("AIOREDIS_DATABASE_URI", pre=True)
    def assemble_jwt_db_connection(
            cls, v: Optional[str], values: dict[str, Any]) -> Any:
        """
        Assemble the cache database connection as URI string
        :param v: Variables to consider
        :type v: str
        :param values: Variables names and its values
        :type values: dict[str, Any]
        :return: Redis URI
        :rtype: RedisDsn
        """
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            user=values.get("REDIS_USERNAME"),
            password=values.get("REDIS_PASSWORD"),
            host=values.get("REDIS_HOST"),
            port=str(values.get("REDIS_PORT")),
        )

    CONTACT_NAME: str = None
    CONTACT_URL: AnyHttpUrl = None
    CONTACT_EMAIL: EmailStr = None
    CONTACT: dict[str, Any]

    @root_validator(pre=True)
    def assemble_contact(cls, values: dict) -> dict:
        """
        Assemble contact information
        :param values: Values of the environment variables
        :type values: dict
        :return: The contact attribute
        :rtype: dict
        """
        contact: dict[str, Any] = {}
        if values.get("CONTACT_NAME"):
            contact["name"] = values["CONTACT_NAME"]
        if values.get("CONTACT_URL"):
            contact["url"] = values["CONTACT_URL"]
        if values.get("CONTACT_EMAIL"):
            contact["email"] = values["CONTACT_EMAIL"]
        values["CONTACT"] = contact
        return {k: v for k, v in values.items() if
                k not in ("CONTACT_NAME", "CONTACT_URL", "CONTACT_EMAIL")}

    DESCRIPTION: str = f"""**FastAPI**, **SQLAlchemy** and **Redis** helps you
     do awesome stuff. 🚀\n\n<img src="data:image/png;base64,{img_b64}"/>"""
    LICENSE_INFO: dict[str, str] = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"}
    TAGS_METADATA: list[dict[str, str]] = [
        {
            "name": "users",
            "description": f"""Operations with users, such as register, get,
             update and delete.\n\n<img src="data:image/png;base64,
             {users_b64}" width="300" height="200"/>"""
        },
        {
            "name": "analyses",
            "description": f"""Manage analyses with creation and get a specific
             analysis on a single or multiple tweets from an specific username.
             \n\n<img src="data:image/png;base64,{analyses_b64}" width="400"
              height="200"/>"""
        },
        {
            "name": "models",
            "description": f"""Manage Machine Learning model with creation and
             get a specific model performance information.
             \n\n<img src="data:image/png;base64,{models_b64}" width="500" 
             height="200"/>"""
        },
        {
            "name": "auth",
            "description": f"""The authentication logic is here as well as
             password recovery and reset.
             \n\n<img src="data:image/png;base64,{auth_b64}" width="150" 
             height="150"/>"""}]

    class Config:
        """
        Config class for Settings
        """
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        case_sensitive = True


settings: Settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings cached
    :return: settings object
    :rtype: Settings
    """
    return Settings()
