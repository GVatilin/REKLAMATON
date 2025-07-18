from .auth import api_router as auth_router
from .healh_check import api_router as healh_check_router
from .user import api_router as user_debag
from .settings import api_router as settings_router
from .upload import api_router as upload_router

list_of_routes = [
    auth_router,
    healh_check_router,
    user_debag,
    settings_router,
    upload_router,
]

__all__ = [
    "list_of_routes",
]