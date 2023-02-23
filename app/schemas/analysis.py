"""
Tweet schema
"""
from typing import Optional

from pydantic import BaseModel


class Analysis(BaseModel):
    pass


class TweetBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class TweetCreate(TweetBase):
    title: str


class TweetUpdate(TweetBase):
    pass


class TweetInDBBase(TweetBase):
    id: int
    title: str
    owner_id: int

    class Config:
        orm_mode = True


class Tweet(TweetInDBBase):
    pass


class TweetInDB(TweetInDBBase):
    pass
