"""Internal cache the Client uses to track guilds, users, and channels
as gateway events (.event[]) come in."""


class ConnectionState:
    def __init__(self, dispatch):
        self._dispatch = dispatch
        self.guilds: dict[int, object] = {}
        self.users: dict[int, object] = {}
        self.channels: dict[int, object] = {}

    def get_guild(self, guild_id: int):
        return self.guilds.get(guild_id)

    def get_channel(self, channel_id: int):
        return self.channels.get(channel_id)

    def parse(self, event_name: str, data: dict):
        """Route a raw gateway payload to a handler and fire the matching
        .event[name=...] callback via self._dispatch."""
        handler = getattr(self, f"parse_{event_name.lower()}", None)
        if handler:
            handler(data)
        else:
            self._dispatch(event_name.lower(), data)

    def parse_message_create(self, data: dict):
        from .models.message import Message
        message = Message.from_payload(data, state=self)
        self._dispatch("message", message)

    def parse_guild_create(self, data: dict):
        from .models.guild import Guild
        guild = Guild.from_payload(data, state=self)
        self.guilds[guild.id] = guild
        self._dispatch("guild_join", guild)

    def parse_ready(self, data: dict):
        self._dispatch("ready")
