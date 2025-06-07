from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.utils.user import create_access_token, register_user_via_google
from app.config import get_settings, DefaultSettings
from app.database.connection import get_session


api_router = APIRouter(prefix="/auth/google", tags=["Google auth"])


@api_router.get("/login")
async def login_via_google(
    request: Request,
    settings: Annotated[DefaultSettings, Depends(get_settings)],
) -> RedirectResponse:
    redirect_uri = request.url_for("auth_google_callback")
    return await settings.google_oauth.google.authorize_redirect(request, redirect_uri)


@api_router.get("/callback")
async def auth_google_callback(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[DefaultSettings, Depends(get_settings)],
) -> RedirectResponse:
    try:
        token = await settings.google_oauth.google.authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=f"OAuth Error: {error.error}")
    
    resp = await settings.google_oauth.google.get("userinfo", token=token)
    user_info = resp.json()

    if not user_info.get("email"):
        raise HTTPException(status_code=400, detail="Google did not send an email")

    await register_user_via_google(session, user_info)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_info.get("email")},
        expires_delta=access_token_expires
    )

    frontend_callback_url = f"http://{settings.VUE_APP_DNS_URL}/auth/google/callback?access_token={access_token}&token_type=bearer"
    return RedirectResponse(url=frontend_callback_url)
