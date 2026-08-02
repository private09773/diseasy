"""Prefix commands: .command[name=, description=], .arg[], .arg_choices[],
.respond(), .respond_ephemeral(), .defer[], .followup()"""
from dataclasses import dataclass, field


@dataclass
class Argument:
    name: str
    type: str = "str"
    required: bool = True
    choices: list[str] = field(default_factory=list)


class Command:
    def __init__(self, callback, *, name: str, description: str = ""):
        self.callback = callback
        self.name = name
        self.description = description
        self.args: list[Argument] = []
        self.checks: list = []
        self.cooldown: tuple[int, int] | None = None

    def arg(self, name: str, type: str = "str", required: bool = True,
            choices: list[str] | None = None) -> "Command":
        self.args.append(Argument(name=name, type=type, required=required,
                                   choices=choices or []))
        return self

    def check(self, permission: str) -> "Command":
        self.checks.append(permission)
        return self

    def cooldown_set(self, rate: int, per: int) -> "Command":
        self.cooldown = (rate, per)
        return self

    async def invoke(self, ctx, *args, **kwargs):
        return await self.callback(ctx, *args, **kwargs)


def command(name: str, description: str = ""):
    """Decorator: @command(name="example", description="example")"""
    def decorator(func) -> Command:
        return Command(func, name=name, description=description)
    return decorator
