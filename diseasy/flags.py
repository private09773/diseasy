"""Bitfield-style flags: gateway Intents and permission Flags."""
from enum import IntFlag, auto


class Intents(IntFlag):
    guilds = auto()
    members = auto()
    moderation = auto()
    messages = auto()
    message_content = auto()
    reactions = auto()
    voice_states = auto()
    presences = auto()

    @classmethod
    def from_names(cls, names: list[str]) -> "Intents":
        """Build a combined Intents value from a list of names,
        e.g. Intents.from_names(["guilds", "messages"])."""
        value = cls(0)
        for name in names:
            value |= cls[name]
        return value


class Permissions(IntFlag):
    administrator = auto()
    manage_messages = auto()
    manage_guild = auto()
    kick_members = auto()
    ban_members = auto()
    send_messages = auto()
    read_message_history = auto()
    mention_everyone = auto()

    @classmethod
    def from_name(cls, name: str) -> "Permissions":
        return cls[name]
