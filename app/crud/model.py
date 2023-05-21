"""
This script provides the data access layer to perform CRUD operations
 on the Model entity in the database
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
    Repository class for Model
    """

    def __init__(self, session: AsyncSession, index_filter: IndexFilter):
        self.session: AsyncSession = session
        self.index_filter: IndexFilter = index_filter
        self.model: Model = Model

    async def read_by_id(self, _id: IdSpecification) -> Optional[Model]:
        """
        Retrieve a model from the database by its id
        :param _id: The id of the model
        :type _id: IdSpecification
        :return: The model with the specified id, or None if no such
         model exists
        :rtype: Optional[Model]
        """
        async with self.session as session:
            try:
                model: Model = await self.index_filter.filter(
                    _id, session, self.model)
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(
                    f"Error at reading model with id: {_id.value}") from db_exc
            return model

    async def read_models(
            self, offset: NonNegativeInt, limit: PositiveInt,
    ) -> Optional[list[Model]]:
        """
        Retrieve a list of models from the database, with pagination
        :param offset: The number of models to skip before starting to
         return models
        :type offset: NonNegativeInt
        :param limit: The maximum number of models to return
        :type limit: PositiveInt
        :return: A list of models
        :rtype: Optional[list[Model]]
        """
        stmt: Select = select(self.model).offset(offset).limit(limit)
        async with self.session as session:
            try:
                results: ScalarResult = await session.scalars(stmt)
                models: list[Model] = results.all()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(
                    f"Error at reading models.\n{str(sa_exc)}") from sa_exc
            return models

    async def create_model(self, model: ModelCreate) -> Optional[Model]:
        """
        Create a new model in the database
        :param model: An object containing the information of the model
         to create
        :type model: ModelCreate
        :return: The created model
        :rtype: Optional[Model]
        """
        model_create: Model = Model(**model.dict())
        async with self.session as session:
            try:
                session.add(model_create)
                await session.commit()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(
                    f"Error at creating model with {model_create.id}"
                ) from sa_exc
            try:
                created_model: Model = await self.read_by_id(IdSpecification(
                    model_create.id))
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            return created_model


async def get_model_repository() -> ModelRepository:
    """
    Create a ModelRepository with an async database session and an
     index filter
    :return: A ModelRepository instance
    :rtype: ModelRepository
    """
    return ModelRepository(await get_session(), await get_index_filter())
