from fastapi import APIRouter, Depends, status, HTTPException, Body, UploadFile, File, Form
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional


from app.config import DefaultSettings, get_settings
from app.database.connection import get_session
from app.schemas import ChatCreateForm
from app.utils.user import get_current_user, User
from app.utils.chats import (
    create_chat_utils,
    get_user_chats_utils,
)
from app.utils.ai_generation import analyze_chat_screenshot


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


@api_router.get('/get_user_chats',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_user_chats(current_user: Annotated[User, Depends(get_current_user)],
                         session: Annotated[AsyncSession, Depends(get_session)]):
    return await get_user_chats_utils(current_user, session)

"""
@api_router.post(
    "/analyze_chat_screenshot",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Non authorized"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal error"}
    }
)
async def analyze_chat_screenshot_endpoint(
    # файл из multipart/form-data
    screenshot: UploadFile = File(..., description="Изображение скриншота (png/jpg/webp)"),
    # дополнительные текстовые поля (Form, чтобы шли в той же multipart форме)
    user_message: Optional[str] = Form(None),
    ocr_method: str = Form("easyocr"),
    current_user: Annotated["User", Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None
):
    # Проверки типа файла (минимальная валидация)
    if screenshot.content_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(status_code=400, detail="Поддерживаются только png/jpeg/webp")

    try:
        # Считываем байты
        image_bytes = await screenshot.read()

        # Передаём в вашу функцию (она принимает Union[bytes, str, Path])
        result = await analyze_chat_screenshot(
            screenshot=image_bytes,
            user_message=user_message,
            ocr_method=ocr_method
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

"""