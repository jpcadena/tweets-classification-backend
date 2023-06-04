"""
This script contains abstract and concrete filter classes for data
 models.
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Union

from pydantic import PositiveInt
from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import benchmark, with_logging
from app.crud.specification import (
    EmailSpecification,
    IdSpecification,
    Specification,
    UsernameSpecification,
)
from app.models.analysis import Analysis
from app.models.model import Model
from app.models.user import User

logger: logging.Logger = logging.getLogger(__name__)


class Filter(ABC):
    """
    Abstract Base Class for creating filters on data models
    """

    @abstractmethod
    async def filter(
            self, spec: Specification, session: AsyncSession,
            model: Union[User, Model, Analysis], field: str
    ) -> Optional[Union[User, Model, Analysis]]:
        """
        Filter method to be implemented by subclasses
        :param spec: Specification to filter by
        :type spec: Specification
        :param session: Async Session for Database
        :type session: AsyncSession
        :param model: The data model to be filtered
        :type model: User, Model or Analysis
        :param field: The field for UniqueFilter
        :type field: str
        :return: An instance of the data model that matches the filter.
         Returns None if no match is found
        :rtype: Optional[Union[User, Model, Analysis]]
        """


class IndexFilter(Filter):
    """
    Filter subclass that filters data models by their ID.
    """

    @with_logging
    @benchmark
    async def filter(
            self, spec: IdSpecification, session: AsyncSession,
            model: Union[User, Model, Analysis], field: Optional[str] = None
    ) -> Optional[Union[User, Model, Analysis]]:
        _id: PositiveInt = spec.value
        async with session as async_session:
            try:
                db_obj = await async_session.get(model, _id)
                logger.info("Retrieving row with id: %s", _id)
                return db_obj
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise sa_exc


class UniqueFilter(Filter):
    """
    Filter subclass that filters data models by a unique field, such as
     username or email.
    """

    @with_logging
    @benchmark
    async def filter(
            self, spec: Union[UsernameSpecification, EmailSpecification],
            session: AsyncSession, model: User, field: str = "email"
    ) -> Union[User, Model, Analysis]:
        stmt: Select
        if field == "username":
            stmt = select(model).where(model.username == spec.value)
        elif field == "email":
            stmt = select(model).where(model.email == spec.value)
        else:
            raise ValueError("Invalid field specified for filtering")
        async with session as async_session:
            try:
                db_obj = (await async_session.scalars(stmt)).one()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise sa_exc
            logger.info("Retrieving row with filter: %s", spec.value)
            return db_obj


async def get_index_filter() -> IndexFilter:
    """
    Factory function that returns an instance of the IndexFilter class
    :return: An instance of the IndexFilter class
    :rtype: IndexFilter
    """
    return IndexFilter()


async def get_unique_filter() -> UniqueFilter:
    """
    Factory function that returns an instance of the UniqueFilter class
    :return: An instance of the UniqueFilter class
    :rtype: UniqueFilter
    """
    return UniqueFilter()
