from sqlalchemy import Column, String, Boolean, UUID, func, DateTime, ForeignKey
from sqlalchemy.orm import validates, relationship
from app.database import DeclarativeBase
import uuid


class Chat(DeclarativeBase):
    __tablename__ = "chats"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    
    name = Column(String)
    author_id = Column(UUID, ForeignKey("users.id"), index=True)
    author = relationship("User")