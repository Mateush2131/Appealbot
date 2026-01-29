from .user import register_user_handlers
from .admin import register_admin_handlers
from .payment import register_payment_handlers
from .start import router as start_router

__all__ = [
    "register_user_handlers",
    "register_admin_handlers", 
    "register_payment_handlers",
    "start_router"
]