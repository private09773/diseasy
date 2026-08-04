"""Cogs — the only {} container: bundles commands + events + lifecycle hooks."""
from .core import Command
from ..slash.core import SlashCommand


class Cog:
    """Subclass this to group related commands/events together.
    Methods decorated with @command(...) or @slash_command(...) inside
    the subclass are collected automatically at instantiation time."""

    def __init__(self):
        self.__cog_commands__: dict[str, Command] = {}
        self.__cog_slash_commands__: dict[str, SlashCommand] = {}
        self.__cog_events__: dict[str, list] = {}
        for attr_name in dir(self.__class__):
            attr = getattr(self, attr_name)
            if isinstance(attr, Command):
                self.__cog_commands__[attr.name] = attr
            elif isinstance(attr, SlashCommand):
                # NEW — did not exist before. Without this, @slash_command
                # methods inside a Cog subclass were silently never
                # collected or registered anywhere.
                self.__cog_slash_commands__[attr.name] = attr
            elif hasattr(attr, "__diseasy_event_name__"):
                event_name = attr.__diseasy_event_name__
                self.__cog_events__.setdefault(event_name, []).append(attr)

    async def cog_load(self):
        """Called once when the cog is added to the client."""

    async def cog_unload(self):
        """Called once when the cog is removed from the client."""

    async def cog_check(self, ctx) -> bool:
        """Global check applied before any command in this cog runs."""
        return True
