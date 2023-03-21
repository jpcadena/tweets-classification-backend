"""
Model CRUD script
"""
import logging
from typing import Optional

from pydantic import PositiveInt, NonNegativeInt
from sqlalchemy import select, Select, ScalarResult
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.exceptions import DatabaseException
from app.crud.filter import IndexFilter, get_index_filter
from app.crud.specification import IdSpecification
from app.db.session import get_session
from app.models.model import Model
from app.schemas.model import ModelCreate

logger: logging.Logger = logging.getLogger(__name__)


class ModelRepository:
    """
    Model repository class
    """

    def __init__(self, session: AsyncSession, index_filter: IndexFilter):
        self.session: AsyncSession = session
        self.index_filter: IndexFilter = index_filter
        self.model: Model = Model

    async def read_by_id(self, _id: IdSpecification) -> Optional[Model]:
        """
        Read a model by its id
        :param _id:
        :type _id: IdSpecification
        :return:
        :rtype: Model
        """
        async with self.session as session:
            try:
                model: Model = await self.index_filter.filter(
                    _id, session, self.model)
            except SQLAlchemyError as db_exc:
                raise DatabaseException(
                    f'Error at reading model with id: {_id.value}') from db_exc
            return model

    async def read_models(
            self, offset: NonNegativeInt, limit: PositiveInt,
    ) -> Optional[list[Model]]:
        """
        Read models information from table
        :param offset: Offset from where to start returning models
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: Model information
        :rtype: Model
        """
        stmt: Select = select(self.model).offset(offset).limit(limit)
        async with self.session as session:
            try:
                results: ScalarResult = await session.scalars(stmt)
                models: list[Model] = results.all()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(
                    f'Error at reading models.\n{str(sa_exc)}') from sa_exc
            return models

    async def create_model(self, model: ModelCreate) -> Optional[Model]:
        """
        Create model into the database
        :param model: Request object representing the model
        :type model: ModelCreate
        :return: Response object representing the created model in the
         database
        :rtype: Model
        """
        model_create: Model = Model(**model.dict())
        async with self.session as session:
            try:
                session.add(model_create)
                await session.commit()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(
                    f"Error at creating model with {model_create.id}") from sa_exc
            try:
                created_model: Model = await self.read_by_id(IdSpecification(
                    model_create.id))
            except SQLAlchemyError as db_exc:
                raise DatabaseException(str(db_exc)) from db_exc
            return created_model


async def get_model_repository() -> ModelRepository:
    """
    Get an instance of the model repository with the given session.
    :return: ModelRepository instance with session associated
    :rtype: ModelRepository
    """
    return ModelRepository(await get_session(), await get_index_filter())
