"""
diseasy/modal.py (v0.3)

Modal — a popup form Discord shows in response to an interaction
(e.g. a button click or slash command), matching Discord's real
modal JSON schema:
  { "type": 9, "data": { "custom_id": ..., "title": ...,
    "components": [ { "type": 1, "components": [
      { "type": 4, "custom_id": ..., "style": 1|2, "label": ...,
        "required": bool, "placeholder": ... } ] } ] } }

Text input style: 1 = short (single line), 2 = paragraph (multi-line).

Usage:
    from diseasy.modal import Modal

    modal = Modal(title="Feedback", custom_id="feedback_modal")
    modal.add_text_input(custom_id="feedback_text", label="Your feedback", style="paragraph")

    @modal.on_submit
    async def handle_submit(interaction, values):
        text = values["feedback_text"]
        await interaction.send(message=f"Thanks! You said: {text}")

    bot.add_modal(modal)

    # Showing it, typically from a button click or slash command:
    @button.on_click
    async def open_form(interaction):
        await interaction.show_modal(modal)
"""

_STYLE_MAP = {"short": 1, "paragraph": 2}


class TextInput:
    def __init__(self, custom_id: str, label: str, style: str = "short",
                 required: bool = True, placeholder: str = None, max_length: int = None):
        if style not in _STYLE_MAP:
            raise ValueError(f"Unknown text input style: {style} (expected 'short' or 'paragraph')")
        self.custom_id = custom_id
        self.label = label
        self.style = style
        self.required = required
        self.placeholder = placeholder
        self.max_length = max_length

    def to_payload(self) -> dict:
        data = {
            "type": 4,
            "custom_id": self.custom_id,
            "style": _STYLE_MAP[self.style],
            "label": self.label,
            "required": self.required,
        }
        if self.placeholder:
            data["placeholder"] = self.placeholder
        if self.max_length:
            data["max_length"] = self.max_length
        return data


class Modal:
    def __init__(self, title: str, custom_id: str):
        self.title = title
        self.custom_id = custom_id
        self.inputs: list[TextInput] = []
        self._callback = None

    def add_text_input(self, custom_id: str, label: str, style: str = "short",
                        required: bool = True, placeholder: str = None,
                        max_length: int = None) -> "Modal":
        self.inputs.append(TextInput(
            custom_id=custom_id, label=label, style=style,
            required=required, placeholder=placeholder, max_length=max_length,
        ))
        return self

    def on_submit(self, func):
        """Decorator: registers the function to run when this modal is submitted."""
        self._callback = func
        return func

    async def invoke(self, interaction, values: dict):
        if self._callback is None:
            raise RuntimeError(f"Modal '{self.custom_id}' has no on_submit handler registered.")
        return await self._callback(interaction, values)

    def to_payload(self) -> dict:
        # Discord requires each text input wrapped in its own action row.
        action_rows = [
            {"type": 1, "components": [text_input.to_payload()]}
            for text_input in self.inputs
        ]
        return {
            "type": 9,  # MODAL
            "data": {
                "custom_id": self.custom_id,
                "title": self.title,
                "components": action_rows,
            },
        }

    @staticmethod
    def parse_submitted_values(interaction_data: dict) -> dict:
        """
        Parses the raw submitted-modal interaction payload into a flat
        {custom_id: value} dict — Discord nests each field inside its
        own action row, this flattens that back out.
        """
        values = {}
        for row in interaction_data.get("components", []):
            for component in row.get("components", []):
                values[component.get("custom_id")] = component.get("value")
        return values
