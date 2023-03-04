"""
Test main script
"""
import pytest
from httpx import AsyncClient, Response

from main import app


@pytest.mark.anyio
async def test_welcome_message():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response: Response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Tomato"}
