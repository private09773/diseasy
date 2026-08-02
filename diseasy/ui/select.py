"""Select menus: .select[type=], .selectoption[], .selectplaceholder(),
.selectmaxvalues(), .selectminvalues()"""
from ..enums import SelectType


class SelectOption:
    def __init__(self, *, value: str):
        self.value = value
        self.label: str | None = None

    def selectoptionlabel(self, text: str) -> "SelectOption":
        self.label = text
        return self

    def to_dict(self) -> dict:
        return {"label": self.label, "value": self.value}


class Select:
    def __init__(self, *, type: str = "string"):
        self.type = SelectType(type)
        self.options: list[SelectOption] = []
        self.placeholder: str | None = None
        self.min_values: int = 1
        self.max_values: int = 1
        self.custom_id: str | None = None
        self.callback = None

    def selectoption(self, option: SelectOption) -> "Select":
        self.options.append(option)
        return self

    def selectplaceholder(self, text: str) -> "Select":
        self.placeholder = text
        return self

    def selectminvalues(self, n: int) -> "Select":
        self.min_values = n
        return self

    def selectmaxvalues(self, n: int) -> "Select":
        self.max_values = n
        return self

    def select_callback(self, func):
        self.callback = func
        return func

    def to_dict(self) -> dict:
        return {
            "type": "select",
            "select_type": self.type.value,
            "options": [o.to_dict() for o in self.options],
            "placeholder": self.placeholder,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "custom_id": self.custom_id,
        }
