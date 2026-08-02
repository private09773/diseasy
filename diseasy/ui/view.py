"""Persistent views: .view[timeout=], .view_item[], .view_check(),
.view_on_timeout(), .view_persistent[], .view_message_id()"""


class View:
    def __init__(self, *, timeout: float | None = 180):
        self.timeout = timeout
        self.items: list = []
        self.persistent: bool = False
        self.message_id: int | None = None
        self._check = None
        self._on_timeout = None

    def view_item(self, item) -> "View":
        if self.persistent and getattr(item, "custom_id", None) is None:
            raise ValueError("Persistent views require every item to have a custom_id.")
        self.items.append(item)
        return self

    def view_check(self, func):
        self._check = func
        return func

    def view_on_timeout(self, func):
        self._on_timeout = func
        return func

    def view_persistent(self, persistent: bool) -> "View":
        if persistent and self.timeout is not None:
            raise ValueError("Persistent views must have timeout=None.")
        self.persistent = persistent
        return self

    def view_message_id(self, message_id: int) -> "View":
        self.message_id = message_id
        return self

    def to_components(self) -> list[dict]:
        return [item.to_dict() for item in self.items]

    async def dispatch(self, interaction):
        """Route an incoming interaction to the matching item's callback,
        after running .view_check() if one is set."""
        if self._check and not await self._check(interaction):
            return
        custom_id = interaction.get("data", {}).get("custom_id")
        for item in self.items:
            if getattr(item, "custom_id", None) == custom_id and item.callback:
                await item.callback(interaction)
                return
