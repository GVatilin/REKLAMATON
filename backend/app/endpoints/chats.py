from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


from app.config import DefaultSettings, get_settings
from app.database.connection import get_session
from app.schemas import ChatCreateForm
from app.utils.user import get_current_user, User
from app.utils.chats import (
    create_chat_utils,

)

api_router = APIRouter(
    prefix="/chat",
    tags=["Chats"]
)


@api_router.post('/create_chat',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def create_chat(chat: Annotated[ChatCreateForm, Body()],
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[AsyncSession, Depends(get_session)]):
    is_success = await create_chat_utils(chat, current_user, session)

    if is_success:
        return {"message": "Chat created"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error creating chat")