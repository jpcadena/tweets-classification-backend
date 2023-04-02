"""
Model evaluation model script
"""
from datetime import datetime

from pydantic import PositiveInt, NonNegativeFloat, PositiveFloat
from sqlalchemy import Column, ForeignKey, Integer, String, BIGINT, Float, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from ..core.config import settings


class Model(Base):
    """
    Class for Machine Learning Model that inherits from SQLAlchemy
     Declarative Base.
    """
    __tablename__ = "model"

    id: PositiveInt = Column(
        Integer, index=True, unique=True, nullable=False, primary_key=True,
        comment="ID of the Model")
    tweet_id: PositiveInt = Column(
        BIGINT, nullable=False, comment="ID of the Tweet")
    model_name: str = Column(
        String, nullable=False, comment="Name of the model")
    accuracy: NonNegativeFloat = Column(
        Float, nullable=False, comment="Accuracy score of the model")
    precision: NonNegativeFloat = Column(
        Float, nullable=False, comment="Precision score of the model")
    recall: NonNegativeFloat = Column(
        Float, nullable=False, comment="Recall score of the model")
    f1_score: NonNegativeFloat = Column(
        Float, nullable=False, comment="F1 score of the model")
    roc_auc: NonNegativeFloat = Column(
        Float, nullable=False,
        comment="Area Under the Receiver Operating Characteristic Curve"
                " for the model")
    computing_time: PositiveFloat = Column(
        Float, nullable=False,
        comment="The time it took to classify the tweet")
    created_at: datetime = Column(
        TIMESTAMP(timezone=False, precision=settings.TS_PRECISION),
        default=datetime.now(), nullable=False, server_default=text("now()"),
        comment="Time the Model was executed")
    analysis_id: Mapped[PositiveInt] = mapped_column(
        Integer, ForeignKey("analysis.id"), nullable=False,
        comment="ID of the Analysis where the model was executed")
