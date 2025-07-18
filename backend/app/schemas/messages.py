from pydantic import BaseModel
from uuid import UUID


class SendMessageForm(BaseModel):
    text: str
    chat_id: UUID