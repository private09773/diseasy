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

    def __init__(self, data: dict, http=None):
        self._data = data
        self._http = http
        self.id = data.get("id")
        self.token = data.get("token")
        # NEW — needed so Bot._dispatch_slash_command can route an
        # incoming interaction to the right registered SlashCommand
        # by name, instead of reaching into interaction._data directly.
        self.command_name = data.get("data", {}).get("name")
        self._options = {
            opt["name"]: opt.get("value")
            for opt in data.get("data", {}).get("options", [])
        }

    def option_from(self, name: str):
        """Equivalent to the notation's <option.from"name">."""
        return self._options.get(name)

    async def send(self, message: str = "", *, embed=None, components=None, ephemeral=False):
        """
        Responds to this interaction. Requires self._http to have
        been set at construction time.
        """
        if self._http is None:
            raise RuntimeError(
                "Interaction has no HTTP client attached — it must be "
                "constructed with Interaction(data, http=client._http)."
            )
        return await self._http.create_interaction_response(
            self.id,
            self.token,
            content=message,
            embeds=[embed] if embed else None,
            components=components,
            ephemeral=ephemeral,
        )


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
