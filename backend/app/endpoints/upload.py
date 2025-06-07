from fastapi import APIRouter,Security, UploadFile, File, HTTPException, Depends, status
from app.config import get_settings, DefaultSettings 
from app.utils.s3_manager import S3Client 
from typing import Annotated
from app.utils.user import get_current_user
from app.database.connection import get_session
from app.database.models import User
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession


def get_s3_client(settings: DefaultSettings = Depends(get_settings)) -> S3Client:
    return settings.s3_client

api_router = APIRouter(
    prefix="/file",
    tags=["file"]
)

@api_router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(
    file: UploadFile = File(...),
    s3_client: S3Client = Depends(get_s3_client),
    user: User = Security(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        file_data = await file.read()
        key = f"uploads/{user.id}/{file.filename}"
        await s3_client.upload_file(key, file_data)
        return {"message": "Файл успешно загружен", "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/test/s3")
async def test_s3_connection(s3_client: S3Client = Depends(get_s3_client)):
    try:
        objects = await s3_client.list_objects()
        return {"objects": objects}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка подключения к S3: {e}"
        )

@api_router.get("/get", response_class=StreamingResponse)
async def get_avatar(
    s3_client: S3Client = Depends(get_s3_client),
    user: User = Security(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    key = f"uploads/{user.id}/avatar.jpg"
    try:
        file_data = await s3_client.get_file(key)
        return StreamingResponse(iter([file_data]), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")