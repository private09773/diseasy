"""<member> — a User scoped to a specific guild, with roles/nick."""
from .user import User


class Member(User):
    __slots__ = ("guild_id", "nick", "roles")

    def __init__(self, *, guild_id: int, nick: str | None = None, roles: list[int] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = guild_id
        self.nick = nick
        self.roles = roles or []

    @property
    def display_name(self) -> str:
        return self.nick or self.name

    @classmethod
    def from_payload(cls, data: dict, *, guild_id: int, state=None) -> "Member":
        user_data = data["user"]
        return cls(
            id=int(user_data["id"]),
            name=user_data["username"],
            discriminator=user_data.get("discriminator", "0"),
            bot=user_data.get("bot", False),
            guild_id=guild_id,
            nick=data.get("nick"),
            roles=[int(r) for r in data.get("roles", [])],
            state=state,
        )
