"""
diseasy/__init__.py (v0.2.3)

Public API surface for the Diseasy package.

FIXED: the previous version of this file imported `setup_logging`
from .logger, but that function was renamed to `set_log_level` back
in the 0.1.1a logging rework — this file was stale and would have
raised an ImportError the moment anything imported diseasy.

NEW (v0.2.3): presence functions (playing/watching/listening/
custom_status) now exposed at the top level, so beginners can write
`from diseasy import playing` instead of needing to know they live
in diseasy.presence.

Merge this with whatever else you already export (embeds, components,
views, etc.) that aren't listed here since I don't have visibility
into those files.
"""

from .client import Client
from .bot import Bot
from .logger import log, set_log_level, log_online, log_offline, friendly_error
from .permissions import Permissions, BotPermissions
from .variables import VARIABLES, register
from .presence import playing, watching, listening, custom_status
from .runtime import resolve, resolve_vars
from . import fetch as fetch_module
from .fetch import fetch, insert, update, delete, set_db_path

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
    "VARIABLES",
    "register",
    "playing",
    "watching",
    "listening",
    "custom_status",
    "resolve",
    "resolve_vars",
    "fetch",
    "insert",
    "update",
    "delete",
    "set_db_path",
]

__version__ = "0.2.3"
