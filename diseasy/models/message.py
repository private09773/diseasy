"""<message> — a single Discord message."""
from ..mixins import Hashable


class Message(Hashable):
    __slots__ = ("id", "content", "author", "channel_id", "guild_id", "edited_at", "_state")

    def __init__(self, *, id: int, content: str, author, channel_id: int,
                 guild_id: int | None = None, edited_at=None, state=None):
        self.id = id
        self.content = content
        self.author = author
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.edited_at = edited_at
        self._state = state

    @property
    def channel(self):
        return self._state.get_channel(self.channel_id)

    @classmethod
    def from_payload(cls, data: dict, *, state=None) -> "Message":
        from .user import User
        return cls(
            id=int(data["id"]),
            content=data.get("content", ""),
            author=User.from_payload(data["author"], state=state),
            channel_id=int(data["channel_id"]),
            guild_id=int(data["guild_id"]) if data.get("guild_id") else None,
            edited_at=data.get("edited_timestamp"),
            state=state,
        )

    def __repr__(self):
        return f"<Message id={self.id} author={self.author!r}>"
