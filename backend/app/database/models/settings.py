from sqlalchemy import Column, String, Boolean, UUID, Time, ForeignKey
from datetime import time

from app.database import DeclarativeBase
import uuid


class Settings(DeclarativeBase):
    __tablename__ = "Settings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )

    user_id = Column(UUID, ForeignKey("Users.id"), index=True)
    text_settings = Column(String, default="")
    start_working = Column(Time, default=time(7, 0))
    end_working = Column(Time, default=time(23, 0))