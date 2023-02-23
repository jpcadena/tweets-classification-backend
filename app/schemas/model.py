"""
Model schema
"""
from typing import Optional

from pydantic import BaseModel


class ModelBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ModelCreate(ModelBase):
    title: str


class ModelUpdate(ModelBase):
    pass


class ModelInDBBase(ModelBase):
    id: int
    title: str
    owner_id: int

    class Config:
        orm_mode = True


class Model(ModelInDBBase):
    pass


class ModelInDB(ModelInDBBase):
    pass
