"""
Model router module for API endpoints.
"""
from fastapi import APIRouter, Depends, status, Path, Body
from fastapi.exceptions import HTTPException
from pydantic import PositiveInt

from app.api.deps import get_current_user
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
    - :param model: Body Object with image_url and caption to be created
    - :type model: ModelCreate
    - :return: Model created with id, image_url, caption,
    timestamp for creation, user ID
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
    - :return: Found Model from logged-in user
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
        current_user: UserAuth = Depends(get_current_user)) -> list[Model]:
    """
    Retrieve all models from the system.
    - :return: All models from logged-in user
    - :rtype: list[Model]
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    models: list[Model] = await ModelService.read_all_models()
    if not models:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This user has no models in the system.')
    return models
