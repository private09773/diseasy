"""
diseasy/__init__.py (v0.2.4ab)

Public API surface for the Diseasy package.

Merge this with whatever else you already export (other embeds/
components/views not covered here).
"""

from .client import Client
from .bot import Bot
from .logger import log, set_log_level, log_online, log_offline, friendly_error
from .permissions import Permissions, BotPermissions
# variables excluded from public API (per your rule)
# from .variables import VARIABLES, register
from .presence import playing, watching, listening, custom_status  # status excluded
# math, commands excluded
from .runtime import resolve, resolve_vars
from .fetch import fetch, insert, update, delete, set_db_path
from .embed import Embed
from .components import Button, Dropdown
from .anti_nuke import (
    ChannelGuard,
    ChannelCreationBlocked,
    get_default_guard,
    set_default_guard,
)

__all__ = [
    "Client",
    "Bot",
    "log",
    "set_log_level",
    "log_online",
    "log_offline",
    "friendly_error",
    "Permissions",
    "BotPermissions",
    # VARIABLES, register excluded
    # playing, watching, listening, custom_status excluded
    "resolve",
    "resolve_vars",
    "fetch",
    "insert",
    "update",
    "delete",
    "set_db_path",
    "Embed",
    "Button",
    "Dropdown",
    "ChannelGuard",
    "ChannelCreationBlocked",
    "get_default_guard",
    "set_default_guard",
]

__version__ = "0.2.4ab"