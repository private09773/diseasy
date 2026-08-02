"""Diseasy — a from-scratch, discord.py-inspired Discord bot library."""

from .client import Client
from .errors import (
    DiseasyException,
    GatewayError,
    HTTPException,
    CommandError,
    CommandNotFound,
    MissingPermissions,
    CommandOnCooldown,
    BadArgument,
    CheckFailure,
    CustomError,
)
from .flags import Intents, Permissions
from .ui.embed import Embed
from .ui.button import Button
from .ui.select import Select, SelectOption
from .ui.modal import Modal, ModalInput
from .ui.view import View
from .ui.components import (
    Container,
    ContainerText,
    ContainerSeparator,
    ContainerImage,
    ContainerThumbnail,
    ContainerSection,
    ContainerGallery,
    ContainerFile,
    ContainerActionRow,
    ContainerSpoiler,
)
from .ui.asset import AssetEmbed, AssetNoEmbed, AssetGetFrom

__version__ = "0.1.0"

__all__ = [
    "Client",
    "Intents",
    "Permissions",
    "Embed",
    "Button",
    "Select",
    "SelectOption",
    "Modal",
    "ModalInput",
    "View",
    "Container",
    "ContainerText",
    "ContainerSeparator",
    "ContainerImage",
    "ContainerThumbnail",
    "ContainerSection",
    "ContainerGallery",
    "ContainerFile",
    "ContainerActionRow",
    "ContainerSpoiler",
    "AssetEmbed",
    "AssetNoEmbed",
    "AssetGetFrom",
    "DiseasyException",
    "GatewayError",
    "HTTPException",
    "CommandError",
    "CommandNotFound",
    "MissingPermissions",
    "CommandOnCooldown",
    "BadArgument",
    "CheckFailure",
    "CustomError",
]
