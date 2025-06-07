from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class UserResponse(BaseModel):
    email: str = Field(unique=True)
    username: str
    premium: bool


class UserDebugResponse(BaseModel):
    id: UUID
    email: str = Field(unique=True)
    username: str
    premium: bool
    password: str


class UserCreateForm(BaseModel):
    email: str = Field(unique=True)
    password: str = Field()
