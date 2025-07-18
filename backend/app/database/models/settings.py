from sqlalchemy import Column, String, Boolean, UUID, Time, ForeignKey
from datetime import time

from app.database import DeclarativeBase
import uuid


class Settings(DeclarativeBase):
    __tablename__ = "settings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )

    user_id = Column(UUID, ForeignKey("users.id"), index=True)