from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


api_router = APIRouter(
    prefix="/question",
    tags=["Question"]
)