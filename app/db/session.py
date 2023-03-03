"""
DB Session script
"""
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, \
    AsyncEngine

from app.core.config import settings
from app.core.decorators import with_logging, benchmark

async_engine: AsyncEngine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, future=True,
    echo=True)


@with_logging
async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Get connection session to the database as a generator
    :return session: Async session for database connection
    :rtype session: AsyncSession
    """
    async with AsyncSession(
            bind=async_engine, expire_on_commit=False) as async_session:
        try:
            yield async_session
        finally:
            await async_session.close()


@with_logging
@benchmark
async def get_session() -> AsyncSession:
    """
    Get connection session to the database
    :return session: Async session for database connection
    :rtype session: AsyncSession
    """
    async for session in get_db():
        return session
