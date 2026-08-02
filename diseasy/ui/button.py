"""Buttons: .button[style=], .buttonlabel(), .buttonemoji(), .buttondisabled[],
.buttoncustomid()"""
from ..enums import ButtonStyle


class Button:
    def __init__(self, *, style: str = "primary"):
        self.style = ButtonStyle(style)
        self.label: str | None = None
        self.emoji: str | None = None
        self.disabled: bool = False
        self.custom_id: str | None = None
        self.callback = None

    def buttonlabel(self, text: str) -> "Button":
        self.label = text
        return self

    def buttonemoji(self, emoji: str) -> "Button":
        self.emoji = emoji
        return self

    def buttondisabled(self, disabled: bool) -> "Button":
        self.disabled = disabled
        return self

    def buttoncustomid(self, custom_id: str) -> "Button":
        self.custom_id = custom_id
        return self

    def button_callback(self, func):
        """Decorator: registers the async callback fired on interaction."""
        self.callback = func
        return func

    def to_dict(self) -> dict:
        return {
            "type": "button",
            "style": self.style.value,
            "label": self.label,
            "emoji": self.emoji,
            "disabled": self.disabled,
            "custom_id": self.custom_id,
        }
