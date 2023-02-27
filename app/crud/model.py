"""
Model CRUD script
"""
from typing import Optional, Union

from pydantic import PositiveInt, NonNegativeInt
from sqlalchemy import select, Select, ScalarResult
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Model
from app.schemas.model import ModelCreate


async def read_model_by_id(
        model_id: int, session: AsyncSession) -> Optional[Model]:
    """
    Read model information from table
    :param model_id: Unique identifier of the model
    :type model_id: int
    :param self.session: Async Session for Database
    :type self.session: AsyncSession
    :return: Model information
    :rtype: Model
    """
    model: Model = await session.get(Model, model_id)
    if not model:
        return None
    return model


async def create_model(
        model: ModelCreate, session: AsyncSession
) -> Union[Model, str]:
    """
    Create model into the database
    :param model: Request object representing the model
    :type model: ModelCreate or ModelSuperCreate
    :return: Response object representing the created model in the
     database
    :rtype: Model or exception
    """
    model_create: Model = Model(**model.dict())
    try:
        session.add(model_create)
        await session.commit()
    except IntegrityError as i_exc:
        return str(i_exc)
    created_model: Model = await read_model_by_id(
        model_create.modelname, session)
    return created_model


async def read_models(
        offset: NonNegativeInt, limit: PositiveInt,
        session: AsyncSession
) -> Optional[list[Model]]:
    """
    Read models information from table
    :param self.session: Async Session for Database
    :type self.session: AsyncSession
    :param offset: Offset from where to start returning models
    :type offset: NonNegativeInt
    :param limit: Limit the number of results from query
    :type limit: PositiveInt
    :return: Model information
    :rtype: Model
    """
    models: list[Model] = None
    stmt: Select = select(Model).offset(offset).limit(limit)
    try:
        results: ScalarResult = await session.scalars(stmt)
        models = results.all()
    except NoResultFound as nrf_exc:
        print(nrf_exc)
    return models
