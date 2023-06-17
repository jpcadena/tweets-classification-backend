"""
Initialization of the database (PostgreSQL) script
"""
import logging

from fastapi import Depends
from sqlalchemy.exc import (
    CompileError,
    DatabaseError,
    DataError,
    DisconnectionError,
    IntegrityError,
    InternalError,
    InvalidatePoolError,
    PendingRollbackError,
)
from sqlalchemy.exc import TimeoutError as SATimeoutError
from sqlalchemy.ext.asyncio import AsyncTransaction

from app.core import config
from app.core.decorators import benchmark, with_logging
from app.crud.user import UserRepository, get_user_repository
from app.db.base_class import Base
from app.db.session import async_engine
from app.models.user import User
from app.schemas.user import UserSuperCreate
from app.utils.utils import hide_email

logger: logging.Logger = logging.getLogger(__name__)


@with_logging
@benchmark
async def create_db_and_tables() -> None:
    """
    Create the database and tables if they don't exist
    :return: None
    :rtype: NoneType
    """
    async with async_engine.connect() as async_connection:
        try:
            transaction: AsyncTransaction = async_connection.begin()
            await transaction.start()
            await async_connection.run_sync(Base.metadata.drop_all)
            await async_connection.run_sync(Base.metadata.create_all)
            await transaction.commit()
        except PendingRollbackError as pr_exc:
            await transaction.rollback()
            logger.error(pr_exc)
        except CompileError as c_exc:
            logger.error(c_exc)
        except DataError as d_exc:
            logger.error(d_exc)
        except IntegrityError as i_exc:
            logger.error(i_exc)
        except InternalError as int_exc:
            logger.error(int_exc)
        except DatabaseError as db_exc:
            logger.error(db_exc)
        except InvalidatePoolError as ip_exc:
            logger.error(ip_exc)
        except DisconnectionError as dc_exc:
            logger.error(dc_exc)
        except SATimeoutError as t_exc:
            logger.error(t_exc)


@with_logging
@benchmark
async def init_db(
        user_repo: UserRepository = Depends(get_user_repository),
        settings: config.Settings = Depends(config.get_settings)
) -> None:
    """
    Initialize the database connection and create the necessary tables.
    :param user_repo: The user repository dependency.
    :type user_repo: UserRepository
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    await create_db_and_tables()
    # user: UserResponse = await user_repo.read_by_email(
    #     EmailSpecification(settings.SUPERUSER_EMAIL))
    # if not user:
    user: UserSuperCreate = UserSuperCreate(
        username=settings.SUPERUSER_EMAIL.split("@")[0],
        email=settings.SUPERUSER_EMAIL,
        first_name=settings.SUPERUSER_FIRST_NAME,
        last_name=settings.SUPERUSER_EMAIL.split("@")[0].capitalize(),
        password=settings.SUPERUSER_PASSWORD,
    )
    superuser: User = await user_repo.create_user(user)
    email: str = await hide_email(superuser.email)
    logger.info("Superuser created with email %s", email)
