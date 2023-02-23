"""
Tweet model script
"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String, BIGINT, Boolean, \
    text, CheckConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped
from app.db.base_class import Base
from ..core.config import settings

if TYPE_CHECKING:
    from .user import User


class Analysis(Base):
    """
    Analysis class model as a table
    """
    __tablename__ = 'analysis'

    id: int = Column(
        Integer, index=True, unique=True, nullable=False, primary_key=True,
        comment='ID of the Analysis')
    tweet_id: int = Column(BIGINT, nullable=False, comment='ID of the Tweet')
    content: str = Column(String(280), nullable=False,
                          comment='The actual UTF-8 text of the status update')
    tweet_username: str = Column(
        String(15), CheckConstraint('char_length(tweet_username) >= 4'),
        nullable=False, comment='Username to identify the user')
    target: bool = Column(
        Boolean(True, 'target_smallint'), nullable=False,
        comment='True if the user is active; otherwise false')
    created_at: datetime = Column(
        TIMESTAMP(timezone=False, precision=settings.TS_PRECISION),
        default=datetime.now(), nullable=False,
        server_default=text("now()"),
        comment='Time the Analysis was performed')
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"),
        nullable=False, comment='ID of the User who performed the Analysis')

    __table_args__ = (
        CheckConstraint(
            settings.USERNAME_CONSTRAINT, name='tweet_username_format'),
    )
