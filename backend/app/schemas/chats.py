from pydantic import BaseModel
from uuid import UUID


class ChatCreateForm(BaseModel):
    name: str
