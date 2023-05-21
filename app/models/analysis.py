"""
Tweet model script
"""
from datetime import datetime

from pydantic import PositiveInt
from sqlalchemy import Column, ForeignKey, Integer, String, BIGINT, Boolean, \
    text, CheckConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db.base_class import Base
from .model import Model
from ..core.config import settings


class Analysis(Base):
    """
    Analysis model class representing the "analysis" table
    """
    __tablename__ = "analysis"

    id: PositiveInt = Column(
        Integer, index=True, unique=True, nullable=False, primary_key=True,
        comment="ID of the Analysis")
    tweet_id: PositiveInt = Column(
        BIGINT, nullable=False, comment="ID of the Tweet")
    content: str = Column(
        String(280), nullable=False,
        comment="The actual UTF-8 text of the status update")
    tweet_username: str = Column(
        String(15), CheckConstraint("char_length(tweet_username) >= 4"),
        nullable=False, comment="Username to identify the user")
    target: bool = Column(
        Boolean(True, "target_smallint"), nullable=False,
        comment="True if the user is active; otherwise false")
    created_at: datetime = Column(
        TIMESTAMP(timezone=False, precision=settings.TS_PRECISION),
        default=datetime.now(), nullable=False, server_default=text("now()"),
        comment="Time the Analysis was performed")
    user_id: Mapped[PositiveInt] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False,
        comment="ID of the User who performed the Analysis")
    models: Mapped[list[Model]] = relationship(lazy="selectin")

    __table_args__ = (
        CheckConstraint(
            settings.DB_TW_USERNAME_CONSTRAINT, name="tweet_username_format"),
    )
