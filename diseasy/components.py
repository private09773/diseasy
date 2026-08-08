"""
diseasy/components.py (v0.2.4)

Button and Dropdown (select menu) components, matching Discord's
real message component JSON schema:
  Button:  {"type": 2, "style": 1-5, "label": "...", "custom_id": "..."}
  Select:  {"type": 3, "custom_id": "...", "options": [...]}

Both route their click/select callback through the SAME Interaction
object used by slash commands — meaning interaction.create_channel()
(built earlier) works identically whether triggered by a button, a
dropdown, or a slash command.

Usage:
    from diseasy.components import Button

    button = Button(label="Create Channel", style="primary", custom_id="create_channel_btn")

    @button.on_click
    async def handle_click(interaction):
        await interaction.create_channel(name="new-channel")

Registration with Bot (so Discord's MESSAGE_COMPONENT interactions
route to the right handler by custom_id) is a separate piece — see
the DEPENDENCY NOTE at the bottom of this file.
"""

_STYLE_MAP = {
    "primary": 1, "secondary": 2, "success": 3, "danger": 4, "link": 5,
}


class Button:
    def __init__(self, label: str, style: str = "primary", custom_id: str = None,
                 disabled: bool = False):
        if style not in _STYLE_MAP:
            raise ValueError(f"Unknown button style: {style} "
                              f"(expected one of {list(_STYLE_MAP)})")
        self.label = label
        self.style = style
        self.custom_id = custom_id or label.lower().replace(" ", "_")
        self.disabled = disabled
        self._callback = None

    def on_click(self, func):
        """Decorator: registers the function to run when this button is clicked."""
        self._callback = func
        return func

    async def invoke(self, interaction):
        if self._callback is None:
            raise RuntimeError(f"Button '{self.custom_id}' has no on_click handler registered.")
        return await self._callback(interaction)

    def to_payload(self) -> dict:
        return {
            "type": 2,
            "style": _STYLE_MAP[self.style],
            "label": self.label,
            "custom_id": self.custom_id,
            "disabled": self.disabled,
        }


class DropdownOption:
    def __init__(self, label: str, value: str, description: str = None):
        self.label = label
        self.value = value
        self.description = description

    def to_payload(self) -> dict:
        data = {"label": self.label, "value": self.value}
        if self.description:
            data["description"] = self.description
        return data


class Dropdown:
    def __init__(self, custom_id: str, placeholder: str = None,
                 min_values: int = 1, max_values: int = 1):
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.options: list[DropdownOption] = []
        self._callback = None

    def add_option(self, label: str, value: str, description: str = None) -> "Dropdown":
        self.options.append(DropdownOption(label=label, value=value, description=description))
        return self

    def on_select(self, func):
        """Decorator: registers the function to run when an option is selected."""
        self._callback = func
        return func

    async def invoke(self, interaction, selected_value: str):
        if self._callback is None:
            raise RuntimeError(f"Dropdown '{self.custom_id}' has no on_select handler registered.")
        return await self._callback(interaction, selected_value)

    def to_payload(self) -> dict:
        return {
            "type": 3,
            "custom_id": self.custom_id,
            "placeholder": self.placeholder,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "options": [o.to_payload() for o in self.options],
        }


# ---------------------------------------------------------------------
# DEPENDENCY NOTE: for a real click/selection to actually reach
# Button.invoke()/Dropdown.invoke(), Bot needs a registry mapping
# custom_id -> component, and state.py's parse_interaction_create
# needs to distinguish MESSAGE_COMPONENT (type 3) interactions from
# APPLICATION_COMMAND (type 2) ones, routing type-3 interactions here
# instead of to the slash command dispatcher. That wiring is the next
# piece to build — not yet done in this file.
# ---------------------------------------------------------------------
