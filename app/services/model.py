"""
Model Service to handle business logic
"""
from typing import Annotated, Optional, Type

from fastapi import Depends
from pydantic import NonNegativeInt, PositiveInt

from app.core.security.exceptions import DatabaseException, ServiceException
from app.crud.model import ModelRepository, get_model_repository
from app.crud.specification import IdSpecification
from app.models.model import Model
from app.schemas.model import Model as ModelResponse
from app.schemas.model import ModelCreate
from app.services import model_to_response


class ModelService:
    """
    Model service class.
    """

    def __init__(self, model_repo: ModelRepository):
        self.model_repo: ModelRepository = model_repo

    async def get_model_by_id(self, model_id: PositiveInt) -> ModelResponse:
        """
        Get model information by model ID.
        :param model_id: Unique identifier of the model
        :type model_id: PositiveInt
        :return: Model information
        :rtype: ModelResponse
        """
        try:
            model: Model = await self.model_repo.read_by_id(
                IdSpecification(model_id))
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(model, ModelResponse)

    async def register_model(self, model: ModelCreate) -> ModelResponse:
        """
        Register a model into the database
        :param model: Request object representing the model
        :type model: ModelCreate
        :return: Response object representing the created model in the
         database
        :rtype: ModelResponse
        """
        try:
            created_model: Model = await self.model_repo.create_model(model)
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(created_model, ModelResponse)

    async def get_models(
            self, offset: NonNegativeInt, limit: PositiveInt
    ) -> Optional[list[ModelResponse]]:
        """
        Retrieve models information from the database
        :param offset: Offset from where to start returning models
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: Models information
        :rtype: Optional[list[ModelResponse]]
        """
        try:
            models: list[Model] = await self.model_repo.read_models(
                offset, limit)
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        found_models: list[ModelResponse] = [
            await model_to_response(model, ModelResponse) for model in models]
        return found_models


async def get_model_service(
        model_repo: ModelRepository = Depends(
            get_model_repository)
) -> ModelService:
    """
    Get an instance of the model service with the given repository.
    :param model_repo: Model repository object for database connection
    :type model_repo: ModelRepository
    :return: ModelService instance with repository associated
    :rtype: ModelService
    """
    return ModelService(model_repo)


ServiceModel: Type[ModelService] = Annotated[
    ModelService, Depends(get_model_service)]
