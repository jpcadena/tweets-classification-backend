"""
Tweet schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

from app.schemas.model import Model


class AnalysisId(BaseModel):
    """
    Analysis ID class that inherits from Pydantic Base Model.
    """
    id: PositiveInt = Field(
        ..., title='Analysis ID', description='ID of the Analysis')


class AnalysisTarget(BaseModel):
    """
    Analysis Target class that inherits from Pydantic Base Model.
    """
    target: bool = Field(
        ..., title='Target (Insecurity)',
        description='True if the user is active; otherwise false')


class AnalysisBase(BaseModel):
    """
    Base Analysis class that inherits from AnalysisTarget.
    """
    tweet_id: PositiveInt = Field(
        ..., title='Tweet ID', description='ID of the Tweet')
    content: str = Field(
        ..., title='Content',
        description='The actual UTF-8 text of the status update',
        max_length=280)
    tweet_username: str = Field(
        ..., title='Tweet Username',
        description='Username to identify the user', min_length=4,
        max_length=15)
    created_at: datetime = Field(
        default_factory=datetime.now, title='Created At',
        description='Time the Analysis was performed')
    user_id: PositiveInt = Field(
        ..., title='User ID',
        description='ID of the User who performed the Analysis')
    models: Optional[list[Model]] = Field(
        default=[], title='Models', description='List of performed model',
        unique_items=True)


class AnalysisCreate(AnalysisTarget, AnalysisBase):
    """
    Class for created Analysis that inherits from AnalysisBase
    """

    class Config:
        """
        Config class for AnalysisCreate
        """
        orm_mode: bool = True
        schema_extra: dict[str, dict] = {
            "example": {
                "tweet_id": 1,
                "content": "Hello, world",
                "tweet_username": "username",
                "created_at": datetime.utcnow(),
                "user_id": 2,
                "models": None,
                "target": False}}


class Analysis(AnalysisTarget, AnalysisBase, AnalysisId):
    """
    Analysis class that inherits from AnalysisId, AnalysisBase and
    AnalysisTarget.
    """

    class Config:
        """
        Config class for Analysis
        """
        orm_mode: bool = True
        schema_extra: dict[str, dict] = {
            "example": {
                "id": 2,
                "tweet_id": 242312391,
                "content": "Hello, world #Ecuador #insecurity",
                "tweet_username": "my_username",
                "created_at": datetime.utcnow(),
                "user_id": 5,
                "models": None,
                "target": False}}
