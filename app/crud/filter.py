"""
Filter script
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Union

from pydantic import PositiveInt
from sqlalchemy import select, Select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import with_logging, benchmark
from app.crud.specification import Specification, IdSpecification, \
    UsernameSpecification, EmailSpecification
from app.models.analysis import Analysis
from app.models.model import Model
from app.models.user import User

logger: logging.Logger = logging.getLogger(__name__)


class Filter(ABC):
    """
    Filter class
    """

    @abstractmethod
    async def filter(
            self, spec: Specification, session: AsyncSession,
            model: Union[User, Model, Analysis], field: str
    ) -> Optional[Union[User, Model, Analysis]]:
        """
        Filter method
        :param spec: specification to filter by
        :type spec: Specification
        :param session: Async Session for Database
        :type session: AsyncSession
        :param model: Datatable model
        :type model: User, Model or Analysis
        :param field: The field for UniqueFilter
        :type field: str
        :return: Datatable model instance
        :rtype: User, Model or Analysis
        """


class IndexFilter(Filter):
    """
    User Filter class based on Filter for ID.
    """

    @with_logging
    @benchmark
    async def filter(
            self, spec: IdSpecification, session: AsyncSession,
            model: Union[User, Model, Analysis], field: str = None
    ) -> Union[User, Model, Analysis]:
        _id: PositiveInt = spec.value
        try:
            db_obj = await session.get(model, _id)
        except SQLAlchemyError as sa_exc:
            logger.error(sa_exc)
            raise sa_exc
        logger.info('Row retrieved with id: %s', _id)
        return db_obj


class UniqueFilter(Filter):
    """
    Unique Filter class based on Filter for Username and Email.
    """

    @with_logging
    @benchmark
    async def filter(
            self, spec: Union[UsernameSpecification, EmailSpecification],
            session: AsyncSession, model: User, field: str = "email"
    ) -> Union[User, Model, Analysis]:
        if field == "username":
            stmt: Select = select(model).where(model.username == spec.value)
        elif field == "email":
            stmt: Select = select(model).where(model.email == spec.value)
        else:
            raise ValueError("Invalid field specified for filtering")
        try:
            db_obj = (await session.scalars(stmt)).one()
        except SQLAlchemyError as sa_exc:
            logger.error(sa_exc)
            raise sa_exc
        logger.info('Row retrieved with filter: %s', spec.value)
        return db_obj


async def get_index_filter() -> IndexFilter:
    """
    Get an IndexFilter instance
    :return: IndexFilter instance
    :rtype: IndexFilter
    """
    return IndexFilter()


async def get_unique_filter() -> UniqueFilter:
    """
    Get an UniqueFilter instance
    :return: UniqueFilter instance
    :rtype: UniqueFilter
    """
    return UniqueFilter()
