from .auth import api_router as auth_router
from .healh_check import api_router as healh_check_router
from .user import api_router as user_debag
from .deadline_task import api_router as deadline_task_router
from .schedule import api_router as schedule_route
from .settings import api_router as settings_router
from .google_auth import api_router as google_router
from .task_groups import api_router as groups_router
from .upload import api_router as upload_router
from .payment import api_router as payment_router

list_of_routes = [
    auth_router,
    healh_check_router,
    user_debag,
    deadline_task_router,
    schedule_route,
    settings_router,
    google_router,
    groups_router,
    upload_router,
    payment_router,
]

__all__ = [
    "list_of_routes",
]