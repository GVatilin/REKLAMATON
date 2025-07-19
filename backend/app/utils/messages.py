from fastapi import APIRouter, Depends, status, HTTPException, Body, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Annotated, Optional
import datetime

from app.database.models import User, Chat, Message
from app.schemas import SendMessageForm
from app.utils.ai_generation import default_ai_answer, form_analyze, partner_ai_answer, chat_analysis_ai_functions

import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


ai_functions = [default_ai_answer, form_analyze, partner_ai_answer]


async def send_message_utils(message: SendMessageForm, author: User, session: AsyncSession, type: int, chat_type: int):
    # 1. Достаем всю историю и делаем из неё одну строку
    query = select(Message).where(Message.chat_id == message.chat_id)
    res = await session.scalars(query)
    history = res.all()

    text = "пользователя" if chat_type == 0 else "собеседника"
    history_str = "\n".join(
        f'Сообщение пользователя: "{m.text}"' if m.is_user
        else f'Сообщение {text}: {m.text}'
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
    ai_response = await ai_functions[type](message.text, history_str)
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


async def chat_analysis_utils(current_user: User, session: AsyncSession, chat_id: UUID):
    query = select(Message).where(Message.chat_id == chat_id)
    res = await session.scalars(query)
    history = res.all()

    history_str = "\n".join(
        f'Сообщение пользователя: "{m.text}"' if m.is_user
        else f'Сообщение собеседника: {m.text}'
        for m in history
    )

    ai_response = await chat_analysis_ai_functions(history_str)

    ai_messages = ai_response.get("messages")
    ans = []
    for message in ai_messages:
        ans.append(message["text"])
    return ans
