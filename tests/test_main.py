"""
Test main script
"""
import pytest
from httpx import AsyncClient, Response

from main import app


@pytest.mark.anyio
async def test_welcome_message() -> None:
    """
    Test welcome_message path operation at main script
    ## Response:
    - `return:` **Welcome message**
    - `rtype:` **Msg**
    """
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response: Response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello, world!"}

# TODO: Add tests for the whole packages.
