from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select

from app.config import DefaultSettings, get_settings
from app.database.connection import get_session
from app.database.models import User, Settings
from app.schemas.settings import EmailUpdateForm, PasswordUpdateForm
from uuid import UUID
from app.schemas import UserTextSettings
from app.schemas.settings import WorkingHoursForm


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_settings().PWD_CONTEXT.verify(plain_password, hashed_password)


async def update_password(id: UUID,updated_password: str, session: AsyncSession) -> bool:
    query = select(User).where(User.id == id)
    result = await session.scalar(query)
    if not result:
        return False
    try:
        hashed_password = get_settings().PWD_CONTEXT.hash(updated_password)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="hashed mistake"
        )
    try:
        setattr(result, "password", hashed_password)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="new password mistake"
        )
    await session.commit()
    return True


async def update_email(id: UUID, updated_email: str, session: AsyncSession) -> bool:
    query = select(User).where(User.id == id)
    result = await session.scalar(query)
    if not result:
        return False
    setattr(result, "email", updated_email)
    await session.commit()
    return True


async def set_text_settings(response: UserTextSettings, current_user: User, session: AsyncSession) -> bool:
    query = select(Settings).where(Settings.user_id == current_user.id)
    result = await session.scalar(query)
    result.text_settings = response.text

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    return True


async def working_hours(response: WorkingHoursForm, current_user: User, session: AsyncSession) -> bool:
    query = select(Settings).where(Settings.user_id == current_user.id)
    result = await session.scalar(query)
    
    result.start_working = response.start_working
    result.end_working = response.end_working

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    return True


async def get_settings(current_user: User, session: AsyncSession):
    query = select(Settings).where(Settings.user_id == current_user.id)
    result = await session.scalar(query)
    return result


async def get_settings_debug(session: AsyncSession):
    query = select(Settings)
    result = await session.scalars(query)
    return result.all()