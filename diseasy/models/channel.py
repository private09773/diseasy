"""<channel> — a messageable text channel."""
from ..abc import Messageable
from ..mixins import Hashable


class TextChannel(Hashable, Messageable):
    __slots__ = ("id", "name", "guild_id", "_state")

    def __init__(self, *, id: int, name: str, guild_id: int | None = None, state=None):
        self.id = id
        self.name = name
        self.guild_id = guild_id
        self._state = state

    @classmethod
    def from_payload(cls, data: dict, *, state=None) -> "TextChannel":
        return cls(
            id=int(data["id"]),
            name=data.get("name", ""),
            guild_id=int(data["guild_id"]) if data.get("guild_id") else None,
            state=state,
        )

    async def send(self, content: str = None, *, embed=None, view=None):
        embeds = [embed.to_dict()] if embed else None
        components = view.to_components() if view else None
        return await self._state._dispatch_http_send(
            self.id, content=content, embeds=embeds, components=components
        )

    def __repr__(self):
        return f"<TextChannel id={self.id} name={self.name!r}>"
