"""Modals: .modal[], .modaltitle(), .modalinput[style=], .modalinputlabel(),
.modalinputrequired[]"""


class ModalInput:
    def __init__(self, *, style: str = "short"):
        self.style = style
        self.label: str | None = None
        self.required: bool = True

    def modalinputlabel(self, text: str) -> "ModalInput":
        self.label = text
        return self

    def modalinputrequired(self, required: bool) -> "ModalInput":
        self.required = required
        return self

    def to_dict(self) -> dict:
        return {"style": self.style, "label": self.label, "required": self.required}


class Modal:
    def __init__(self):
        self.title: str | None = None
        self.inputs: list[ModalInput] = []
        self.callback = None

    def modaltitle(self, text: str) -> "Modal":
        self.title = text
        return self

    def add_input(self, modal_input: ModalInput) -> "Modal":
        self.inputs.append(modal_input)
        return self

    def modal_callback(self, func):
        self.callback = func
        return func

    def to_dict(self) -> dict:
        return {"title": self.title, "inputs": [i.to_dict() for i in self.inputs]}
