"""
Test user API router script
"""
from unittest import mock, TestCase

from fastapi.testclient import TestClient
from httpx import Response
from pydantic import EmailStr

from app.api.api_v1.router.user import router
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate

client: TestClient = TestClient(router)


class TestUserAPI(TestCase):
    def test_create_user(self):
        with mock.patch(
                "app.api.api_v1.router.user.send_new_account_email"
        ) as mock_send_email:
            user: UserCreate = UserCreate(
                username="test_user",
                email=EmailStr("test_user@example.com"),
                password="secret_password",
                first_name="Test",
                last_name="User")
            response: Response = client.post(
                f"{settings.API_V1_STR}/users",
                headers={"Content-Type": "application/json"}, data=user.dict())
            assert response.status_code == 201
            assert "id" in response.json()
            assert response.json()["username"] == user.username
            assert response.json()["email"] == user.email
            assert response.json()["first_name"] == user.first_name
            assert response.json()["middle_name"] is None
            assert response.json()["last_name"] == user.last_name
            mock_send_email.assert_called_once_with(
                user.email, user.username)

    def test_get_user_me(self):
        user = User.create(
            username="test_user",
            email="test_user@example.com",
            password="secret_password",
            first_name="Test",
            last_name="User")
        access_token = user.create_access_token()
        response = client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        assert "id" in response.json()
        assert response.json()["username"] == user.username
        assert response.json()["email"] == user.email
        assert response.json()["first_name"] == user.first_name
        assert response.json()["middle_name"] is None
        assert response.json()["last_name"] == user.last_name

    def test_get_users(self):
        User.create(
            username="test_user_1",
            email="test_user_1@example.com",
            password="secret_password",
            first_name="Test 1",
            last_name="User 1")
        User.create(
            username="test_user_2",
            email="test_user_2@example.com",
            password="secret_password",
            first_name="Test 2",
            last_name="User 2")
        response: Response = client.get(
            f"{settings.API_V1_STR}/users",
            headers={"Content-Type": "application/json"})
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_user_by_id(self):
        user = User.create(
            username="test_user",
            email="test_user@example.com",
            password="secret_password",
            first_name="Test",
            last_name="User")
        response: Response = client.get(
            f"{settings.API_V1_STR}/users/{user.id}",
            headers={"Content-Type": "application/json"})
        assert response.status_code == 200
        assert "id" in response.json()
        assert response.json()["username"] == user.username
        assert response.json()["email"] == user.email
        assert response.json()["first_name"] == user.first_name
        assert response.json()["middle_name"] is None
