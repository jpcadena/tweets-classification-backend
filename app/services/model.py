"""
Model Service to handle business logic
"""
from typing import Optional

from fastapi import Depends
from pydantic import PositiveInt, NonNegativeInt
from sqlalchemy.exc import SQLAlchemyError

from app.crud.model import ModelRepository, get_model_repository
from app.crud.specification import IdSpecification
from app.models import Model
from app.schemas.model import ModelCreate, Model as ModelResponse
from app.services import model_to_response


class ModelService:
    """
    Model service class.
    """

    def __init__(self, model_repo: ModelRepository):
        self.model_repo: ModelRepository = model_repo

    async def get_model_by_id(self, model_id: PositiveInt) -> ModelResponse:
        """
        Get model information with the correct schema for response
        :param model_id: Unique identifier of the model
        :type model_id: PositiveInt
        :return: Model information
        :rtype: ModelResponse
        """
        model: Model = await self.model_repo.read_by_id(IdSpecification(
            model_id))
        return await model_to_response(model, ModelResponse)

    async def register_model(self, model: ModelCreate) -> ModelResponse:
        """
        Create model into the database
        :param model: Request object representing the model
        :type model: ModelCreate or ModelSuperCreate
        :return: Response object representing the created model in the
         database
        :rtype: ModelCreateResponse or exception
        """
        try:
            created_model = await self.model_repo.create_model(model)
        except SQLAlchemyError as sa_exc:
            raise sa_exc
        return await model_to_response(created_model, ModelResponse)

    async def get_models(
            self, offset: NonNegativeInt, limit: PositiveInt
    ) -> Optional[list[ModelResponse]]:
        """
        Read models information from table
        :param offset: Offset from where to start returning models
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: Model information
        :rtype: ModelResponse
        """
        try:
            models: list[Model] = await self.model_repo.read_models(
                offset, limit)
        except SQLAlchemyError as nrf_exc:
            raise nrf_exc
        found_models: list[ModelResponse] = [
            await model_to_response(model, ModelResponse) for model in models]
        return found_models


async def get_model_service(
        model_repo: ModelRepository = Depends(
            get_model_repository)) -> ModelService:
    """
    Get an instance of the model service with the given repository.
    :param model_repo: Model repository object for database connection
    :type model_repo: ModelRepository
    :return: ModelService instance with repository associated
    :rtype: ModelService
    """
    return ModelService(model_repo)
