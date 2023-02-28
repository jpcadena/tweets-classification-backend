"""
Filter script
"""
from abc import ABC, abstractmethod
from typing import Optional, Union

from pydantic import PositiveInt
from sqlalchemy import select, Select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.specification import Specification, IdSpecification, \
    UsernameSpecification, EmailSpecification
from app.models import User, Model, Analysis


class Filter(ABC):
    """
    Filter class
    """

    @abstractmethod
    async def filter(
            self, spec: Specification, session: AsyncSession,
            model: Union[User, Model, Analysis]
    ) -> Optional[Union[User, Model, Analysis]]:
        """
        Filter method
        :param spec: specification to filter by
        :type spec: Specification
        :param self.session: Async Session for Database
        :type self.session: AsyncSession
        :param model: Datatable model
        :type model: User, Model or Analysis
        :return: Datatable model instance
        :rtype: User, Model or Analysis
        """


class IndexFilter(Filter):
    """
    User Filter class based on Filter for ID.
    """

    async def filter(
            self, spec: IdSpecification, session: AsyncSession,
            model: Union[User, Model, Analysis]
    ) -> Optional[Union[User, Model, Analysis]]:
        _id: PositiveInt = spec.value
        return await session.get(model, _id)


class UniqueFilter(Filter):
    """
    Unique Filter class based on Filter for Username and Email.
    """

    async def filter(
            self, spec: Union[UsernameSpecification, EmailSpecification],
            session: AsyncSession, model: User
    ) -> Optional[Union[User, Model, Analysis]]:
        stmt: Select = select(model).where(model.username == spec.value)
        try:
            db_obj = (await session.scalars(stmt)).one()
        except SQLAlchemyError as exc:
            raise exc
        return db_obj


async def get_index_filter() -> IndexFilter:
    """

    :return: IndexFilter instance
    :rtype: IndexFilter
    """
    return IndexFilter()


async def get_unique_filter() -> UniqueFilter:
    """

    :return: UniqueFilter instance
    :rtype: UniqueFilter
    """
    return UniqueFilter()
