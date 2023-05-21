"""
Machine Learning Model schema
"""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, PositiveInt, NonNegativeFloat, \
    PositiveFloat


class ModelID(BaseModel):
    """
    Schema for representing a Model's ID.
    """
    id: PositiveInt = Field(
        ..., title="Model ID", description="ID of the Model")


class ModelBase(BaseModel):
    """
    Base schema for representing a Model.
    """
    tweet_id: PositiveInt = Field(
        ..., title="Tweet ID", description="ID of the Tweet")
    model_name: str = Field(
        ..., title="Model Name", description="Name of the model")
    accuracy: NonNegativeFloat = Field(
        ..., title="Accuracy", description="Accuracy score of the model")
    precision: NonNegativeFloat = Field(
        ..., title="Precision", description="Precision score of the model")
    recall: NonNegativeFloat = Field(
        ..., title="Recall", description="Recall score of the model")
    f1_score: NonNegativeFloat = Field(
        ..., title="F1 Score", description="F1 score of the model")
    roc_auc: NonNegativeFloat = Field(
        ..., title="ROC AUC",
        description="Area Under the Receiver Operating Characteristic Curve"
                    " for the model")
    computing_time: PositiveFloat = Field(
        ..., title="Computing Time",
        description="The time it took to classify the tweet")


class ModelCreatedAt(BaseModel):
    """
    Schema for representing the creation timestamp of a Model.
    """
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now, title="Created At",
        description="Time the Model was executed")


class ModelCreate(ModelCreatedAt, ModelBase):
    """
    Schema for creating a Model record
    """
    analysis_id: Optional[PositiveInt] = Field(
        default=None, title="Analysis ID",
        description="ID of the Analysis where the model was executed")

    class Config:
        """
        Config class for ModelCreate
        """
        orm_mode: bool = True
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "tweet_id": 24578931,
                "model_name": "Logistic Regression",
                "accuracy": 0.84,
                "precision": 0.94,
                "recall": 0.85,
                "f1_score": 0.89,
                "roc_auc": 0.99,
                "computing_time": 0.03,
                "analysis_id": 1}}


class Model(ModelCreate, ModelID):
    """
    Schema for representing a Model.
    """

    class Config:
        """
        Config class for Model
        """
        orm_mode: bool = True
        schema_extra: dict[str, dict[str, Any]] = {
            "example": {
                "id": 5,
                "tweet_id": 24578931,
                "model_name": "Logistic Regression",
                "accuracy": 0.84,
                "precision": 0.94,
                "recall": 0.85,
                "f1_score": 0.89,
                "roc_auc": 0.99,
                "computing_time": 0.03,
                "created_at": datetime.utcnow(),
                "analysis_id": 2}}
