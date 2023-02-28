"""
Init DB script
"""
from fastapi import Depends
from sqlalchemy.exc import CompileError, DataError, DatabaseError, \
    DisconnectionError, IntegrityError, InternalError, InvalidatePoolError, \
    PendingRollbackError, TimeoutError as SATimeoutError
from sqlalchemy.ext.asyncio import AsyncTransaction

from app.core.config import settings
from app.crud.user import UserRepository, get_user_repository
from app.db.base_class import Base
from app.db.session import async_engine
from app.models import User
from app.schemas.user import UserSuperCreate
from app.utils import hide_email


async def create_db_and_tables() -> None:
    """
    Create database and tables without duplicating them.
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
            print(pr_exc)
        except CompileError as c_exc:
            print(c_exc)
        except DataError as d_exc:
            print(d_exc)
        except IntegrityError as i_exc:
            print(i_exc)
        except InternalError as int_exc:
            print(int_exc)
        except DatabaseError as db_exc:
            print(db_exc)
        except InvalidatePoolError as ip_exc:
            print(ip_exc)
        except DisconnectionError as dc_exc:
            print(dc_exc)
        except SATimeoutError as t_exc:
            print(t_exc)


async def init_db(
        user_repo: UserRepository = Depends(get_user_repository)) -> None:
    """
    Initialization of the database connection
    :param user_repo: Dependency injection for user repository
    :type user_repo: UserRepository
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
    print('Superuser created with email', email)
