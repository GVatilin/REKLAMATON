from sqlalchemy import Column, String, Boolean, UUID, func, DateTime, ForeignKey

from app.database import DeclarativeBase
import uuid


class Message(DeclarativeBase):
    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    
    chat_id = Column(UUID, ForeignKey("chats.id"), index=True)
    text = Column(String)
    date = Column(DateTime)
