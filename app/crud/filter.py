"""
Main script
"""
from abc import ABC, abstractmethod
from typing import Optional, Union, Callable

from pydantic import EmailStr, PositiveInt
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import Specification, IdSpecification, UsernameSpecification, \
    EmailSpecification
from app.models import User


class Filter(ABC):
    """
    Filter class
    """

    @abstractmethod
    async def filter(
            self, spec: Specification, session: AsyncSession
    ) -> Optional[User]:
        """
        Filter method
        :param spec: specification to filter by
        :type spec: Specification
        :param self.session: Async Session for Database
        :type self.session: AsyncSession
        :return: User instance from database
        :rtype: User
        """


class IndexFilter(Filter):
    """
    User Filter class based on Filter for ID.
    """

    async def filter(
            self, spec: IdSpecification, session: AsyncSession
    ) -> Optional[User]:
        _id: PositiveInt = spec.value
        return await session.get(User, _id)


class UniqueFilter(Filter):
    """
    Unique Filter class based on Filter for Username and Email.
    """

    async def filter(
            self, spec: Union[UsernameSpecification, EmailSpecification],
            session: AsyncSession
    ) -> Optional[User]:
        unique_field: Union[str, EmailStr] = spec.value
        stmt: Select = select(User).where(User.username == unique_field)
        user: User = (await session.scalars(stmt)).one()
        return user


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


async def get_filter(filter_type: str) -> Filter:
    """

    :param filter_type:
    :type filter_type: str
    :return: Filter instance
    :rtype: Filter
    """
    filter_factories: dict[str, Callable[[], Filter]] = {
        'index': get_index_filter, 'unique': get_unique_filter}
    factory_function = filter_factories[filter_type]
    return factory_function()
