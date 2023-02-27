"""
Init DB script
"""
from sqlalchemy.exc import CompileError, DataError, DatabaseError, \
    DisconnectionError, IntegrityError, InternalError, InvalidatePoolError, \
    PendingRollbackError, TimeoutError as SATimeoutError
from sqlalchemy.ext.asyncio import AsyncSession, AsyncTransaction

from app.core.config import settings
from app.db.base_class import Base
from app.db.session import async_engine
from app.models import User
from app.schemas.user import UserSuperCreate
from app.services.user import UserService
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


async def init_db(async_session: AsyncSession) -> None:
    """
    Initialization of the database connection
    :param async_session:
    :type async_session:
    :return: None
    :rtype: NoneType
    """
    await create_db_and_tables()
    print("init_db")
    user_service: UserService = UserService(async_session)
    user = await user_service.get_user_by_email(settings.SUPERUSER_EMAIL)
    if not user:
        user_in: UserSuperCreate = UserSuperCreate(
            username=settings.SUPERUSER_EMAIL.split("@")[0],
            email=settings.SUPERUSER_EMAIL,
            first_name=settings.SUPERUSER_FIRST_NAME,
            last_name=settings.SUPERUSER_EMAIL.split("@")[0].capitalize(),
            password=settings.SUPERUSER_PASSWORD,
        )
        superuser: User = await user_service.register_user(user_in)
        email: str = await hide_email(superuser.email)
        print('Superuser created with email', email)
