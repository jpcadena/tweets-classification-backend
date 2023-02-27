"""
Model router module for API endpoints.
"""
from fastapi import APIRouter, Depends, status, Path, Body, Query
from fastapi.exceptions import HTTPException
from pydantic import PositiveInt, NonNegativeInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_user_service
from app.schemas.model import Model, ModelCreate
from app.schemas.user import UserAuth
from app.services.model import ModelService

router: APIRouter = APIRouter(prefix='/models', tags=['models'])


@router.post('', response_model=Model,
             status_code=status.HTTP_201_CREATED)
async def create_model(
        model: ModelCreate = Body(
            ..., title='New model', description='New model to create'),
        current_user: UserAuth = Depends(get_current_user)
) -> Model:
    """
    Create a new model into the system.
    - :param model: Body Object with tweet_id, model_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time and
      relationship with Analysis: analysis_id (OPTIONAL)
    - :type model: ModelCreate
    - :return: Model created with id, tweet_id, model_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time, relationship
      with Analysis: analysis_id and its creation timestamp
    - :rtype: Model
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    auth_user_id: PositiveInt = current_user.id
    created_model: Model = await ModelService.create_model(
        model, auth_user_id)
    return created_model


@router.get('/{model_id}', response_model=Model)
async def get_model(model_id: PositiveInt = Path(
    ..., title='ModelCreate ID',
    description='ID of the ModelCreate to searched',
    example=1), current_user: UserAuth = Depends(get_current_user)
) -> Model:
    """
    Search for specific Model by ID from the system.
    - :param model_id: Path Parameter of Model ID to search
    - :type model_id: PydanticObjectId
    - :return: Found Model from logged-in user with id, tweet_id,
     model_name, accuracy, precision, recall, f1_score, roc_auc,
      computing_time, analysis_id and its creation timestamp
    - :rtype: Model
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    found_model: ModelCreate = await ModelService.read_model_by_id(model_id)
    if not found_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'ModelCreate with ID {model_id} '
                                   f'not found in the system.')
    model: Model = Model(**found_model.dict())
    return model


@router.get('', response_model=list[Model])
async def get_models(
        skip: NonNegativeInt = Query(
            0, title='Skip', description='Skip users', example=0),
        limit: PositiveInt = Query(
            100, title='Limit', description='Limit pagination', example=100),
        session: AsyncSession = Depends(get_user_service),
        current_user: UserAuth = Depends(get_current_user)) -> list[Model]:
    """
    Retrieve all models from the system.
    - :param skip: Offset from where to start returning models
    - :type skip: NonNegativeInt
    - :param limit: Limit the number of results from query
    - :type limit: PositiveInt
    - :return: All models from logged-in user with id, tweet_id,
     model_name, accuracy, precision, recall, f1_score, roc_auc,
      computing_time, analysis_id and its creation timestamp
    - :rtype: list[Model]
    \f
    :param session: Dependency method for async Postgres connection
    :type session: AsyncSession
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    model_service: ModelService = ModelService(session)
    models: list[Model] = await model_service.get_models(skip, limit)
    if not models:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This user has no models in the system.')
    return models
