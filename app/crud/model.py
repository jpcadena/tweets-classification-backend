"""
Model CRUD script
"""
import logging
from typing import Optional

from fastapi import Depends
from pydantic import PositiveInt, NonNegativeInt
from sqlalchemy import select, Select, ScalarResult
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.filter import IndexFilter, get_index_filter
from app.crud.specification import IdSpecification
from app.db.session import get_session
from app.models import Model
from app.schemas.model import ModelCreate


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

        :param _id:
        :type _id: IdSpecification
        :return:
        :rtype: Model
        """
        return await self.index_filter.filter(_id, self.session, self.model)

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
        try:
            results: ScalarResult = await self.session.scalars(stmt)
            models: list[Model] = results.all()
        except NoResultFound as nrf_exc:
            logging.error(nrf_exc)
            raise nrf_exc
        return models

    async def create_model(self, model: ModelCreate) -> Optional[Model]:
        """
        Create model into the database
        :param model: Request object representing the model
        :type model: ModelCreate or ModelSuperCreate
        :return: Response object representing the created model in the
         database
        :rtype: Model
        """
        model_create: Model = Model(**model.dict())
        try:
            self.session.add(model_create)
            await self.session.commit()
        except SQLAlchemyError as sa_exc:
            logging.error(
                "Database Error for model with id: %s.\n%s",
                model_create.id, sa_exc)
            raise sa_exc
        created_model: Model = await self.read_by_id(IdSpecification(
            model_create.id))
        return created_model


async def get_model_repository(
        session: AsyncSession = Depends(get_session)
) -> ModelRepository:
    """
    Get an instance of the model repository with the given session.
    :param session: Session object for database connectio n
    :type session: AsyncSession
    :return: ModelRepository instance with session associated
    :rtype: ModelRepository
    """
    return ModelRepository(session, await get_index_filter())
