from fastapi import APIRouter, Depends, status, HTTPException, Body, Path
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID


from app.schemas import SendMessageForm
from app.utils.user import get_current_user, User
from app.database.connection import get_session
from app.utils.messages import (
    send_message_utils,
    get_messages_from_chat_utils,
)

api_router = APIRouter(
    prefix="/message",
    tags=["Message"]
)


@api_router.post('/send',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def send_message(message: Annotated[SendMessageForm, Body()],
                       current_user: Annotated[User, Depends(get_current_user)],
                       session: Annotated[AsyncSession, Depends(get_session)]):
    return await send_message_utils(message, current_user, session)


@api_router.get('/get_messages_from_chat/{chat_id}',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_messages_from_chat(current_user: Annotated[User, Depends(get_current_user)],
                                 session: Annotated[AsyncSession, Depends(get_session)],
                                 chat_id: UUID = Path(..., description="Введите ID чата, чтобы получить все сообщения")):
    return await get_messages_from_chat_utils(chat_id, current_user, session)