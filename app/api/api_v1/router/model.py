"""
Model router module for API endpoints.
This module handles the routing for model-related API endpoints,
 including creating, reading, and listing models.
"""
from fastapi import APIRouter, status, Path, Body, Query
from fastapi.exceptions import HTTPException
from pydantic import PositiveInt, NonNegativeInt

from app.api.deps import CurrentUser
from app.core.security.exceptions import ServiceException
from app.schemas.model import Model, ModelCreate
from app.services.model import ServiceModel

# pylint: disable=unused-argument
router: APIRouter = APIRouter(prefix="/models", tags=["models"])


@router.post("", response_model=Model, status_code=status.HTTP_201_CREATED)
async def create_model(
        model_service: ServiceModel, current_user: CurrentUser,
        model: ModelCreate = Body(
            ..., title="New model", description="New model to create")
) -> Model:
    """
    Create a new model into the system.
    - `:param model:` **Body Object with tweet_id, model_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time and
      relationship with Analysis: analysis_id (OPTIONAL)**
    - `:type model:` **ModelCreate**
    - `:return:` **Model created with id, tweet_id, model_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time, relationship
      with Analysis: analysis_id and its creation timestamp**
    - `:rtype:` **Model**
    \f
    :param model_service: Dependency method for Model service object
    :type model_service: ServiceModel
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    try:
        created_model: Model = await model_service.register_model(model)
    except ServiceException as serv_exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error at creating model.\n{str(serv_exc)}"
        ) from serv_exc
    return created_model


@router.get("/{model_id}", response_model=Model)
async def get_model(
        model_service: ServiceModel, current_user: CurrentUser,
        model_id: PositiveInt = Path(
            ..., title="Model ID", description="ID of the Model to searched",
            example=1)
) -> Model:
    """
    Retrieves a specific Model by its ID.
    - `:param model_id:` **Path Parameter of Model ID to be retrieved**
    - `:type model_id:` **PositiveInt**
    - `:return:` **Found Model from logged-in user with id, tweet_id,
     model_name, accuracy, precision, recall, f1_score, roc_auc,
      computing_time, analysis_id and its creation timestamp**
    - `:rtype:` **Model**
    \f
    :param model_service: Dependency method for Model service object
    :type model_service: ServiceModel
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    found_model: Model = await model_service.get_model_by_id(model_id)
    if not found_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {model_id} not found in the system.")
    return found_model


@router.get("", response_model=list[Model])
async def get_models(
        model_service: ServiceModel, current_user: CurrentUser,
        skip: NonNegativeInt = Query(
            default=0, title="Skip", description="Number of models to skip",
            example=0),
        limit: PositiveInt = Query(
            default=100, title="Limit",
            description="Maximum number of models to return", example=100)
) -> list[Model]:
    """
    Retrieves all Models, with pagination.
    - `:param skip:` **Number of models to skip**
    - `:type skip:` **NonNegativeInt**
    - `:param limit:` **Maximum number of models to return**
    - `:type limit:` **PositiveInt**
    - `:return:` **All models from logged-in user with id, tweet_id,
     model_name, accuracy, precision, recall, f1_score, roc_auc,
      computing_time, analysis_id and its creation timestamp**
    - `:rtype:` **list[Model]**
    \f
    :param model_service: Dependency method for Model Service
    :type model_service: ServiceModel
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    models: list[Model] = await model_service.get_models(skip, limit)
    if not models:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="This user has no models in the system.")
    return models
