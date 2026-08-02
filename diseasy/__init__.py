"""
diseasy/__init__.py

Public API surface for the Diseasy package.
Merge this with whatever you already export — don't overwrite
existing exports (embeds, components, views, etc.) that aren't
listed here since I don't have visibility into those files.
"""

from .client import Client
from .bot import Bot
from .logger import log, setup_logging
from .permissions import Permissions
from .variables import VARIABLES, register

__all__ = [
    "Client",
    "Bot",
    "log",
    "setup_logging",
    "Permissions",
    "VARIABLES",
    "register",
]

__version__ = "0.1.1"
