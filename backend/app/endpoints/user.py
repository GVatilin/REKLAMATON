from app.database.models import User
from app.database.connection import get_session
from app.schemas import UserResponse, UserDebugResponse
from app.utils.user import get_current_user

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from typing import Annotated


api_router = APIRouter(
    prefix="/user",
    tags=["User"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@api_router.get("/debug/users_table/", response_model=list[UserDebugResponse])
async def get_users_debug(
    session: AsyncSession = Depends(get_session)
) -> list[UserDebugResponse]:
    query = select(User)
    result = await session.scalars(query)
    return result.all()


@api_router.get("/debug/get_users_by_email1/", response_model=UserResponse)
async def get_user_by_email1(email: str, db: AsyncSession = Depends(get_session)) -> UserResponse:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_CONFLICT,
            detail="Пользователь не найден",
        )
    return db_user


async def get_user_by_email_fun(email: str, db: AsyncSession = Depends(get_session)) -> User | None:
    stmt = select(User).where(User.email == email)

    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()

    return db_user


@api_router.delete("", response_model=UserResponse)
async def delete_user_by_email(email: str, db: AsyncSession = Depends(get_session)) -> UserResponse:
    async with db.begin():
        db_user = await get_user_by_email_fun(email, db)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь не найден",
            )
        await db.delete(db_user)
    return db_user
