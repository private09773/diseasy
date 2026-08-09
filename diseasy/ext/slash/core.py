"""Slash commands: .slashcommand[name=, description=], .slashoption[],
<option.from""> variable access, .slashsubcommand[], .slashgroup[],
.autocomplete[]"""
from dataclasses import dataclass, field


# Discord's real slash command option types (numeric, per Discord's
# API docs) — options now use these directly instead of friendly
# string names like "str"/"user".
OPTION_TYPES = {
    "1": "SUB_COMMAND",
    "2": "SUB_COMMAND_GROUP",
    "3": "STRING",
    "4": "INTEGER",
    "5": "BOOLEAN",
    "6": "USER",
    "7": "CHANNEL",
    "8": "ROLE",
    "9": "MENTIONABLE",
    "10": "NUMBER",
    "11": "ATTACHMENT",
}


@dataclass
class SlashOption:
    name: str
    type: str = "3"  # STRING, matching Discord's real default expectation
    required: bool = True
    description: str = ""

    def __post_init__(self):
        if self.type not in OPTION_TYPES:
            raise ValueError(
                f"Unknown option type: '{self.type}'. Must be one of "
                f"{list(OPTION_TYPES.keys())} (Discord's real numeric "
                f"option type codes — e.g. '3' for STRING, '6' for USER)."
            )


class Interaction:
    """Wraps a raw interaction payload and exposes <option.from""> access."""

    def __init__(self, data: dict, http=None):
        self._data = data
        self._http = http
        self.id = data.get("id")
        self.token = data.get("token")
        self.type = data.get("type")  # 2 = command, 3 = component, 5 = modal submit
        self.command_name = data.get("data", {}).get("name")
        self.custom_id = data.get("data", {}).get("custom_id")
        self.values = data.get("data", {}).get("values", [])
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

    async def create_channel(self, name: str, type: int = 0):
        """
        Creates a text channel (type=0) in the guild this interaction
        came from, guarded automatically against nuke-bot-style abuse.
        """
        from ..anti_nuke import get_default_guard

        guild_id = self._data.get("guild_id")
        if guild_id is None:
            raise RuntimeError("This interaction has no guild_id — "
                                "create_channel() only works in a guild.")

        guard = get_default_guard()
        guard.check(guild_id, name)

        result = await self._http.create_guild_channel(guild_id, name=name, type=type)
        guard.record_creation(guild_id)
        return result

    async def show_modal(self, modal):
        """
        Shows a modal in response to this interaction. Must be the
        interaction's first response — Discord doesn't allow showing
        a modal after already sending a message response.
        """
        if self._http is None:
            raise RuntimeError(
                "Interaction has no HTTP client attached — it must be "
                "constructed with Interaction(data, http=client._http)."
            )
        return await self._http.respond_with_modal(self.id, self.token, modal.to_payload())


class SlashCommand:
    def __init__(self, callback, *, name: str, description: str = ""):
        self.callback = callback
        self.name = name
        self.description = description
        self.options: list[SlashOption] = []
        self.autocomplete_handlers: dict[str, callable] = {}

    def slashoption(self, name: str, type: str = "3", required: bool = True,
                    description: str = "") -> "SlashCommand":
        """
        type: Discord's real numeric option type code, as a string.
        e.g. "3" = STRING, "4" = INTEGER, "5" = BOOLEAN, "6" = USER,
        "7" = CHANNEL, "8" = ROLE, "9" = MENTIONABLE, "10" = NUMBER,
        "11" = ATTACHMENT.
        """
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
                # CHANGED: type is now cast to a real int for Discord's
                # API — previously this sent the friendly string name
                # directly, which Discord's real API would reject.
                {"name": o.name, "type": int(o.type), "required": o.required,
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
