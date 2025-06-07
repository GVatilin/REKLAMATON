import secrets
import string
import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy import select
from app.database.models import User
from app.utils.user import verify_password

@pytest.mark.asyncio
class TestUserRegistration:
    async def test_register_success(self, client: AsyncClient):
        """
        Проверяет успешную регистрацию нового пользователя.
        """
        response = await client.post(
            "/user/register",
            json={
                "email": "new_user@example.com",
                "username": "new_user",
                "password": "secure_password"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() is None

    async def test_register_duplicate(self, client: AsyncClient):
        """
        Проверяет, что повторная регистрация с тем же email/username возвращает 400.
        """
        data = {
            "email": "dup_user@example.com",
            "username": "dup_user",
            "password": "password123"
        }
        await client.post("/user/register", json=data)
        response = await client.post("/user/register", json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Username or email already exists"}

    async def test_register_invalid_payload(self, client: AsyncClient):
        """
        Проверяет, что при отсутствии обязательного поля (пароля) возвращается 422.
        """
        response = await client.post(
            "/user/register",
            json={"email": "invalid@example.com", "username": "invalid_user"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_password_hashing_and_verification(self, client: AsyncClient, session):
        """
        Проверяет, что пароль сохраняется в базе в захэшированном виде,
        не совпадает с исходным, может быть проверен и имеет длину >= 8.
        """
        raw_password = "very_secure_password"
        email = "hash_user@example.com"
        username = "hash_user"
        response = await client.post(
            "/user/register",
            json={"email": email, "username": username, "password": raw_password}
        )
        assert response.status_code == status.HTTP_201_CREATED
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one()
        assert user.password != raw_password
        assert verify_password(raw_password, user.password)
        assert len(user.password) >= 8

    async def test_password_too_short(self, client: AsyncClient):
        """
        Проверяет, что при пароле короче 8 символов возвращается 422.
        """
        response = await client.post(
            "/user/register",
            json={"email": "short_pwd@example.com", "username": "shortpwd", "password": "short"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_invalid_email_format(self, client: AsyncClient):
        """
        Проверяет, что при некорректном формате email возвращается 422.
        """
        response = await client.post(
            "/user/register",
            json={"email": "not-an-email", "username": "bademail", "password": "validPass123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_create_10(self, client: AsyncClient, session):
        """
        Создает 10 уникальных пользователей и проверяет, что все они в базе.
        """
        emails = []
        for i in range(10):
            email = f"user_{i}@example.com"
            username = f"user_{i}"
            emails.append(email)
            response = await client.post(
                "/user/register",
                json={"email": email, "username": username, "password": "12345678"}
            )
            assert response.status_code == status.HTTP_201_CREATED

        result = await session.execute(select(User.email).where(User.email.in_(emails)))
        found = {row[0] for row in result.all()}
        assert set(emails) == found
    async def test_registration_random(self, client: AsyncClient):
        """
        Создает 20 случайных пользователей с уникальным email, username и паролем,
        проверяет, что нет ответов 500+ и всего получено 20 ответов.
        """
        statuses = []
        for _ in range(20):
            rand_str = secrets.token_urlsafe(8)
            email = f"{rand_str}@example.com"
            username = f"user_{rand_str}"
            pwd_chars = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(pwd_chars) for _ in range(12))

            response = await client.post(
                "/user/register",
                json={"email": email, "username": username, "password": password}
            )
            statuses.append(response.status_code)
            assert response.status_code < 500

        assert len(statuses) == 20