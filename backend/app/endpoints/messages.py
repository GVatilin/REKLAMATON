from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


api_router = APIRouter(
    prefix="/message",
    tags=["Message"]
)
