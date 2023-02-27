"""
Services initialization package
"""
from typing import TypeVar, Union

from app.models import User, Model, Analysis
from app.schemas import ModelCreate, AnalysisCreate
from app.schemas.user import UserResponse, UserCreateResponse, \
    UserUpdateResponse

T = TypeVar('T', UserResponse, UserCreateResponse, UserUpdateResponse,
            AnalysisCreate, ModelCreate)


async def model_to_response(
        model: Union[User, Analysis, Model], response_model: T) -> T:
    """
    Converts a User object to a Pydantic response model
    :param model: Object from Pydantic Base Model class
    :type model: User or Model
    :param response_model: Response model
    :type response_model: T
    :return: Model inherited from SQLAlchemy Declarative Base
    :rtype: T
    """
    return response_model.from_orm(model)
