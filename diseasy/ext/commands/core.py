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
    """Wraps a raw interaction payload and exposes <option.from""> access.

    UPDATED: added self._http (passed in at construction), self.id/
    self.token (pulled from the raw payload — Discord's real
    INTERACTION_CREATE payload includes "id" and "token" at the top
    level), and a real send() method that calls the interaction
    response endpoint via HTTPClient.create_interaction_response().

    This requires state.py's parse_interaction_create to construct
    Interaction(data, http=self._client._http) — confirmed added
    there earlier in this conversation.
    """

    def __init__(self, data: dict, http=None):
        self._data = data
        self._http = http
        self.id = data.get("id")
        self.token = data.get("token")
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


# ---------------------------------------------------------------------
# Regular (prefix) commands — added because ext/commands/__init__.py
# imports Command, Argument, and command from this file, and none of
# those existed here before.
# ---------------------------------------------------------------------

@dataclass
class Argument:
    name: str
    required: bool = True
    default: object = None


class Command:
    def __init__(self, callback, *, name: str, description: str = ""):
        self.callback = callback
        self.name = name
        self.description = description
        self.arguments: list[Argument] = []

    def argument(self, name: str, required: bool = True, default=None) -> "Command":
        self.arguments.append(Argument(name=name, required=required, default=default))
        return self

    async def invoke(self, ctx, *args, **kwargs):
        return await self.callback(ctx, *args, **kwargs)


def command(name: str, description: str = ""):
    """Decorator: @command(name="ping", description="Replies with pong")"""
    def decorator(func) -> Command:
        return Command(func, name=name, description=description)
    return decorator
