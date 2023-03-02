"""
Token Model for the Redis database
"""
from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    Token class based on Pydantic Base Model.
    """
    key: str = Field(..., title='Key',
                     description='Refresh token key based on User ID and JTI')
    token: str = Field(..., title='Token',
                       description='Refresh token retrieved from login')

    class Config:
        """
        Config class for Token.
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                'key': "63aefa38afda3a176c1e3562:ce0f27c1-c559-45b1-b016",
                'token': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}}
