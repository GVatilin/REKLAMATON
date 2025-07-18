from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException,Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import DefaultSettings, get_settings
from app.database.connection import get_session
from app.schemas import (
    RegistrationForm,
    Token,
    UserResponse,
)
from app.database.models import User
from app.utils.user import (
    authenticate_user,
    create_access_token,
    get_current_user,
    register_user,
)

api_router = APIRouter(prefix="/user", tags=["User"])


@api_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Username or email already exists",
        },
    },
)
async def registration(
    registration_form: Annotated[RegistrationForm, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    is_success = await register_user(session, registration_form)
    if not is_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )


@api_router.post(
    "/token",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect email or password",
        },
    },
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[DefaultSettings, Depends(get_settings)],
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@api_router.get(
    "/me",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect username or password",
        },
    },
    summary="Get active user information",
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return current_user