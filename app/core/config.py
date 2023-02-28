"""
Core config script
"""
from functools import lru_cache
from typing import Any, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, \
    validator, \
    RedisDsn


class Settings(BaseSettings):
    """
    Settings class based on Pydantic Base Settings
    """
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

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
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str],
                               values: dict[str, Any]) -> Any:
        """
        Assemble the database connection as URI string
        :param v: Variables to consider
        :type v: str
        :param values: Variables names and its values'
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
            # port=str(values.get("POSTGRES_PORT")),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    TS_PRECISION: int
    EMAIL_CONSTRAINT: str = r"email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'"
    PHONE_CONSTRAINT: str = r"phone_number ~* '^\+[0-9]{1,15}$'"
    USERNAME_CONSTRAINT: str = r"tweet_username ~* '^[a-zA-Z0-9_]+$'"
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    MAIL_SUBJECT: str
    MAIL_TIMEOUT: float
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/assets/etemplates"
    EMAILS_ENABLED: bool = False
    SUPERUSER_EMAIL: EmailStr
    SUPERUSER_FIRST_NAME: str
    SUPERUSER_PASSWORD: str
    ENCODING: str = "UTF-8"
    OPENAPI_FILE_PATH: str = "/openapi.json"

    REDIS_HOST: str
    REDIS_USERNAME: str
    REDIS_PASSWORD: str
    REDIS_PORT: int
    AIOREDIS_DATABASE_URI: Optional[RedisDsn] = None

    @validator("AIOREDIS_DATABASE_URI", pre=True)
    def assemble_jwt_db_connection(cls, v: Optional[str],
                               values: dict[str, Any]) -> Any:
        """
        Assemble the cache database connection as URI string
        :param v: Variables to consider
        :type v: str
        :param values: Variables names and its values'
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
            port=str(values.get('REDIS_PORT')),
        )

    class Config:
        """
        Config class for Settings
        """
        env_file: str = ".env"
        env_file_encoding: str = 'utf-8'
        case_sensitive = True


settings = Settings()


@lru_cache()
def get_setting() -> Settings:
    """
    Get settings cached
    :return: settings object
    :rtype: Settings
    """
    return Settings()
