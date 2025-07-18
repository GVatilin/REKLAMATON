from fastapi import APIRouter, Depends, status, HTTPException, Body, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Annotated, Optional
import datetime

from app.database.models import User, Chat, Message
from app.schemas import SendMessageForm
from app.utils.ai_generation import default_ai_answer

import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def send_message_utils(message: SendMessageForm, author: User, session: AsyncSession):
    # 1. Достаем всю историю и делаем из неё одну строку
    query = select(Message).where(Message.chat_id == message.chat_id)
    res = await session.scalars(query)
    history = res.all()

    history_str = "\n".join(
        f'Сообщение пользователя: "{m.text}"' if m.is_user
        else f'Сообщение помощника: {m.text}'
        for m in history
    )

    user_msg = Message(
        chat_id=message.chat_id,
        text=message.text,
        is_user=True,
        date=datetime.datetime.now()
    )
    session.add(user_msg)
    await session.commit()

    # 2. Запрашиваем ответ у AI
    ai_response = await default_ai_answer(message.text, history_str)
    ai_text = ai_response.get("text") if isinstance(ai_response, dict) else str(ai_response)

    ai_msg = Message(
        chat_id=message.chat_id,
        text=ai_text,
        is_user=False,
        date=datetime.datetime.now()
    )
    session.add(ai_msg)
    await session.commit()

    return True



async def get_messages_from_chat_utils(chat_id: UUID, current_user: User, session: AsyncSession):
    query = select(Message).where(Message.chat_id == chat_id)
    result = await session.scalars(query)
    return result.all()