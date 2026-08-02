"""<user> — a Discord user."""
from ..mixins import Hashable


class User(Hashable):
    __slots__ = ("id", "name", "discriminator", "bot", "_state")

    def __init__(self, *, id: int, name: str, discriminator: str = "0", bot: bool = False, state=None):
        self.id = id
        self.name = name
        self.discriminator = discriminator
        self.bot = bot
        self._state = state

    @classmethod
    def from_payload(cls, data: dict, *, state=None) -> "User":
        return cls(
            id=int(data["id"]),
            name=data["username"],
            discriminator=data.get("discriminator", "0"),
            bot=data.get("bot", False),
            state=state,
        )

    def __repr__(self):
        return f"<User id={self.id} name={self.name!r}>"
