"""
Services initialization package
"""
from typing import Optional, TypeVar, Union

from app.models.analysis import Analysis
from app.models.model import Model
from app.models.user import User
from app.schemas.analysis import Analysis as AnalysisResponse
from app.schemas.analysis import AnalysisCreate
from app.schemas.model import Model as ModelResponse
from app.schemas.model import ModelCreate
from app.schemas.user import (
    UserCreateResponse,
    UserResponse,
    UserUpdateResponse,
)

T = TypeVar("T", UserResponse, UserCreateResponse, UserUpdateResponse,
            AnalysisCreate, AnalysisResponse, ModelCreate, ModelResponse)


async def model_to_response(
        model: Union[User, Analysis, Model], response_model: T
) -> Optional[T]:
    """
    Converts a model object to a Pydantic response model
    :param model: Object from Pydantic Base Model class
    :type model: Union[User, Analysis, Model]
    :param response_model: Response model
    :type response_model: T
    :return: Model inherited from SQLAlchemy Declarative Base
    :rtype: Optional[T]
    """
    if not model:
        return None
    return response_model.from_orm(model)
