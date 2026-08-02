"""Enumerations used across Diseasy."""
from enum import Enum, IntEnum


class OpCode(IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class ButtonStyle(str, Enum):
    primary = "primary"
    secondary = "secondary"
    success = "success"
    danger = "danger"
    link = "link"


class ComponentType(str, Enum):
    container = "container"
    text = "text"
    separator = "separator"
    image = "image"
    thumbnail = "thumbnail"
    section = "section"
    gallery = "gallery"
    file = "file"
    action_row = "action_row"
    spoiler = "spoiler"
    button = "button"
    select = "select"
    modal = "modal"


class SelectType(str, Enum):
    string = "string"
    user = "user"
    role = "role"
    channel = "channel"
    mentionable = "mentionable"


class OptionType(str, Enum):
    str = "str"
    int = "int"
    bool = "bool"
    user = "user"
    channel = "channel"
    role = "role"
    attachment = "attachment"
