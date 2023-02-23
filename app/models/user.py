"""
User model script
"""
from datetime import datetime, date
from typing import Optional
from pydantic import EmailStr
from sqlalchemy import Boolean, Column, Integer, String, CheckConstraint, Date, \
    text, Enum
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship, Mapped
from app.db.base_class import Base
from .analysis import Analysis
from ..core.config import settings
from ..schemas.gender import Gender


class User(Base):
    """
    User class model as a table
    """
    __tablename__ = "users"

    id: int = Column(
        Integer, index=True, unique=True, nullable=False, primary_key=True,
        comment='ID of the User')
    username: str = Column(
        String(15), CheckConstraint('char_length(username) >= 4'),
        unique=True, nullable=False, comment='Username to identify the user')
    email: EmailStr = Column(
        String(320), CheckConstraint('char_length(email) >= 3'),
        unique=True, nullable=False,
        comment='Preferred e-mail address of the User')
    first_name: str = Column(String(50), nullable=False,
                             comment='First name(s) of the User')
    middle_name: Optional[str] = Column(
        String(50), nullable=True, comment='Middle name(s) of the User')
    last_name: str = Column(String(100), nullable=False,
                            comment='Last name(s) of the User')
    password: str = Column(
        String(100), nullable=False, comment='Hashed password of the User')
    gender: Optional[Gender] = Column(
        Enum(Gender), nullable=True,comment='Gender of the User')
    birthdate: Optional[date] = Column(
        Date, nullable=True, comment='Birthday of the User')
    phone_number: Optional[str] = Column(
        String(16), nullable=True,
        comment='Preferred telephone number of the User')
    city: Optional[str] = Column(
        String(100), nullable=True, comment='City for address of the User')
    country: Optional[str] = Column(
        String(100), CheckConstraint('char_length(country) >= 4'),
        nullable=True, comment='Country for address of the User')
    is_active: bool = Column(
        Boolean(), default=True, nullable=False, server_default=text("true"),
        comment='True if the user is active; otherwise false')
    is_superuser: bool = Column(
        Boolean(), default=False, nullable=False, server_default=text("false"),
        comment='True if the user is super user; otherwise false')
    created_at: datetime = Column(
        TIMESTAMP(timezone=False, precision=settings.TS_PRECISION),
        default=datetime.now(), nullable=False,
        server_default=text("now()"), comment='Time the User was created')
    updated_at: datetime = Column(
        TIMESTAMP(timezone=False, precision=settings.TS_PRECISION),
        nullable=True, comment='Time the User was updated')
    analyses: Mapped[list[Analysis]] = relationship(lazy="selectin")

    __table_args__ = (
        CheckConstraint(settings.EMAIL_CONSTRAINT, name='email_format'),
        CheckConstraint(settings.PHONE_CONSTRAINT, name='phone_number_format')
    )
