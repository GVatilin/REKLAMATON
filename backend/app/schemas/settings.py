from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError
from datetime import datetime, timedelta
from uuid import UUID
from datetime import time
from typing import Optional


class EmailUpdateForm(BaseModel):
    password: str
    email: str = Field(unique=True)


class PasswordUpdateForm(BaseModel):
    oldpassword: str
    password: str


class WorkingHoursForm(BaseModel):
    start_working: time
    end_working: time


class SettingsDebug(BaseModel):
    id: UUID
    user_id: UUID
    text_settings: str
    start_working: time
    end_working: time