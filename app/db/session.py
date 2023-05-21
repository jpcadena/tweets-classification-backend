"""
Database session script
"""
import logging
from typing import Any, AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, \
    AsyncEngine

from app.core.config import settings
from app.core.decorators import with_logging, benchmark

logger: logging.Logger = logging.getLogger(__name__)
async_engine: AsyncEngine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, future=True,
    echo=True)


@with_logging
async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Get an asynchronous session to the database as a generator
    :return session: Async session for database connection
    :rtype session: AsyncSession
    """
    async_session: AsyncSession = AsyncSession(
        bind=async_engine, expire_on_commit=False)
    try:
        yield async_session
        await async_session.commit()
    except SQLAlchemyError as exc:
        logger.error(exc)
        await async_session.rollback()
        raise exc


@with_logging
@benchmark
async def get_session() -> AsyncSession:
    """
    Get an asynchronous session to the database
    :return session: Async session for database connection
    :rtype session: AsyncSession
    """
    async for session in get_db():
        return session
