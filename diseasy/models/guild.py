"""<guild> — a Discord server, holding its channels and member count."""
from ..mixins import Hashable


class Guild(Hashable):
    __slots__ = ("id", "name", "owner_id", "member_count", "channels", "_state")

    def __init__(self, *, id: int, name: str, owner_id: int, member_count: int = 0, state=None):
        self.id = id
        self.name = name
        self.owner_id = owner_id
        self.member_count = member_count
        self.channels: dict[int, object] = {}
        self._state = state

    @classmethod
    def from_payload(cls, data: dict, *, state=None) -> "Guild":
        from .channel import TextChannel
        guild = cls(
            id=int(data["id"]),
            name=data["name"],
            owner_id=int(data["owner_id"]),
            member_count=data.get("member_count", 0),
            state=state,
        )
        for chan_data in data.get("channels", []):
            channel = TextChannel.from_payload(chan_data, state=state)
            guild.channels[channel.id] = channel
            if state:
                state.channels[channel.id] = channel
        return guild

    def __repr__(self):
        return f"<Guild id={self.id} name={self.name!r}>"
