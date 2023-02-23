"""
Message schema
"""

from pydantic import BaseModel


class Msg(BaseModel):
    """
    Base class for Messages.
    """
    msg: str
