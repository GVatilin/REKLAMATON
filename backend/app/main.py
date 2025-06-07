from logging import getLogger
from fastapi import FastAPI
from uvicorn import run
from app.config import DefaultSettings, get_settings
from app.endpoints import list_of_routes
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
logger = getLogger(__name__)


def bindRoutes(application: FastAPI, setting: DefaultSettings) -> None:
     for route in list_of_routes:
       application.include_router(route, prefix=setting.PATH_PREFIX)


def getApp() -> FastAPI:
    description = "Микросервис для создания расписания."

    application = FastAPI(
        docs_url="/api/v1/swagger",
        openapi_url="/api/v1/openapi",
        version="1.0.0",
        title="Chrono",
        description=description,
    )

    settings = get_settings()
    bindRoutes(application, settings)
    application.state.settings = settings
    return application


app = getApp()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key="your_random_secret_key",
)

if __name__ == "__main__":
    settings_for_application = get_settings()
    run(
        "main:app",
        port=settings_for_application.BACKEND_PORT,
        reload=True,
        reload_dirs=["app"],
        log_level="debug",
        host=settings_for_application.BACKEND_HOST,
    )
