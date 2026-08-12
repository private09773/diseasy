"""
diseasy/__init__.py

Public API surface for the Diseasy package.
Everything was exported here, including status, math, commands, and variables.
"""

from .client import Client
from .bot import Bot
from .logger import log, set_log_level, log_online, log_offline, friendly_error
from .permissions import Permissions, BotPermissions
from .variables import VARIABLES, register
from .presence import playing, watching, listening, custom_status
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
from .math import add, subtract, multiply, divide
from .commands import Command, CommandGroup

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
    "Embed",
    "Button",
    "Dropdown",
    "ChannelGuard",
    "ChannelCreationBlocked",
    "get_default_guard",
    "set_default_guard",
    "add",
    "subtract",
    "multiply",
    "divide",
    "Command",
    "CommandGroup",
]

__version__ = "0.2.3"