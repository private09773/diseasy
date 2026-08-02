"""Command groups + subcommands: .commandgroup[], .commandgroup_sub[]"""
from .core import Command


class CommandGroup:
    def __init__(self, *, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.subcommands: dict[str, Command] = {}

    def subcommand(self, name: str, description: str = ""):
        def decorator(func) -> Command:
            cmd = Command(func, name=name, description=description)
            self.subcommands[name] = cmd
            return cmd
        return decorator
