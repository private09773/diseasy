"""Internal cache the Client uses to track guilds, users, and channels
as gateway events (.event[]) come in."""


class _BasicUser:
    """
    Minimal stand-in for the bot's own user object, built from
    Discord's real READY payload shape (data["user"]["id"/"username"]).

    ASSUMPTION FLAG: I don't have confirmation that a real User model
    exists elsewhere in your codebase (e.g. diseasy/models/user.py).
    If one does, this should be replaced with User.from_payload(...)
    the same way parse_message_create uses Message.from_payload(...)
    and parse_guild_create uses Guild.from_payload(...) — this class
    is a fallback so client.user.name at least works today.
    """
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.name = data.get("username")
        self.discriminator = data.get("discriminator")


class ConnectionState:
    def __init__(self, client):
        self._client = client
        self._dispatch = client.dispatch
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
        """
        CHANGED (v0.2.3): now actually sets self._client.user from
        the READY payload — previously this only dispatched "ready"
        with no data, meaning client.user was never set at all, and
        logger.py's log_online() would always print "bot" as a
        fallback instead of the real bot name.
        """
        user_data = data.get("user", {})
        self._client.user = _BasicUser(user_data)
        self._dispatch("ready")

    def parse_interaction_create(self, data: dict):
        from .ext.slash.core import Interaction
        interaction = Interaction(data, http=self._client._http)
        self._dispatch("interaction_create", interaction)
