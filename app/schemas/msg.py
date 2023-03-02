"""
Message schema
"""
from pydantic import BaseModel, Field


class Msg(BaseModel):
    """
    Base class for Messages.
    """
    msg: str = Field(..., title='Message', description='Message to display')

    class Config:
        """
        Config class for Msg.
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {'msg': "Hello, World!!!"}}
