__all__ = (
    "register_users_commands_handlers",
    "register_users_photos_handlers",
    "register_users_receipts_handlers",
    "register_users_categories_handlers",
    "register_users_other_handlers",
)

from .commands import register_users_commands_handlers
from .other import register_users_other_handlers
from .photos import register_users_photos_handlers
from .receipts import register_users_receipts_handlers
from .categories import register_users_categories_handlers
