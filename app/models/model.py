# """
# Model evaluation model script
# """
# from typing import TYPE_CHECKING
# from sqlalchemy import Column, ForeignKey, Integer, String
# from sqlalchemy.orm import relationship
# from app.db.base_class import Base
#
# if TYPE_CHECKING:
#     from .user import User
#
#
# class Model(Base):
#     __tablename__ = 'model'
#     id: int = Column(Integer, primary_key=True, index=True)
#     title: str = Column(String, index=True)
#     description: str = Column(String, index=True)
#     # owner_id: int = Column(Integer, ForeignKey("users.id"))
