from fastapi import APIRouter
from starlette import status


api_router = APIRouter(tags=["Health check"])


@api_router.get(
    "/health_check/ping",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    return {"status": "ok"}
