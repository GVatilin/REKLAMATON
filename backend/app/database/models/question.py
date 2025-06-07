from sqlalchemy import Column, String, Boolean, UUID, Time, ForeignKey, Integer, JSON
from app.database import DeclarativeBase
import uuid
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import validates

class Question(DeclarativeBase):
    __tablename__ = "Question"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    description = Column(String)
    answers = Column(MutableList.as_mutable(JSON), default=[])
    type = Column(Integer)         #0 - один ответ правильный, 1 - несколько ответов
    right_answers = Column(MutableList.as_mutable(JSON), default=[]) 



class AIQuestion(DeclarativeBase):
    __tablename__ = "AIQuestion"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    description = Column(String)
