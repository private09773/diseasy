"""Slash commands: .slashcommand[name=, description=], .slashoption[],
<option.from""> variable access, .slashsubcommand[], .slashgroup[],
.autocomplete[]"""
from dataclasses import dataclass, field


@dataclass
class SlashOption:
    name: str
    type: str = "str"
    required: bool = True
    description: str = ""


class Interaction:
    """Wraps a raw interaction payload and exposes <option.from""> access."""

    def __init__(self, data: dict):
        self._data = data
        self._options = {
            opt["name"]: opt.get("value")
            for opt in data.get("data", {}).get("options", [])
        }

    def option_from(self, name: str):
        """Equivalent to the notation's <option.from"name">."""
        return self._options.get(name)


class SlashCommand:
    def __init__(self, callback, *, name: str, description: str = ""):
        self.callback = callback
        self.name = name
        self.description = description
        self.options: list[SlashOption] = []
        self.autocomplete_handlers: dict[str, callable] = {}

    def slashoption(self, name: str, type: str = "str", required: bool = True,
                    description: str = "") -> "SlashCommand":
        self.options.append(SlashOption(name=name, type=type, required=required,
                                         description=description))
        return self

    def autocomplete(self, option: str):
        def decorator(func):
            self.autocomplete_handlers[option] = func
            return func
        return decorator

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "options": [
                {"name": o.name, "type": o.type, "required": o.required,
                 "description": o.description}
                for o in self.options
            ],
        }

    async def invoke(self, interaction: Interaction):
        return await self.callback(interaction)


def slash_command(name: str, description: str = ""):
    """Decorator: @slash_command(name="example", description="example")"""
    def decorator(func) -> SlashCommand:
        return SlashCommand(func, name=name, description=description)
    return decorator
