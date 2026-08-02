"""Embeds v2 — the container-based component system:
.container[], .containertext[], .containerseperator, .container_src.image[],
.containersection[], .containergallery[], .containerfile[], .containeractionrow[],
.containerspoiler[]"""


class ContainerText:
    def __init__(self, content: str):
        self.content = content

    def to_dict(self) -> dict:
        return {"type": "text", "content": self.content}


class ContainerSeparator:
    def to_dict(self) -> dict:
        return {"type": "separator"}


class ContainerImage:
    def __init__(self, source: str):
        self.source = source

    def to_dict(self) -> dict:
        return {"type": "image", "source": self.source}


class ContainerThumbnail:
    def __init__(self, source: str):
        self.source = source

    def to_dict(self) -> dict:
        return {"type": "thumbnail", "source": self.source}


class ContainerSection:
    def __init__(self, *, accessory=None):
        self.items: list = []
        self.accessory = accessory

    def add_item(self, item) -> "ContainerSection":
        self.items.append(item)
        return self

    def to_dict(self) -> dict:
        data = {"type": "section", "items": [i.to_dict() for i in self.items]}
        if self.accessory is not None:
            data["accessory"] = self.accessory.to_dict()
        return data


class ContainerGallery:
    def __init__(self, assets: list):
        self.assets = assets

    def to_dict(self) -> dict:
        return {"type": "gallery", "assets": [a.to_dict() for a in self.assets]}


class ContainerFile:
    def __init__(self, source: str):
        self.source = source

    def to_dict(self) -> dict:
        return {"type": "file", "source": self.source}


class ContainerActionRow:
    def __init__(self, items: list):
        self.items = items

    def to_dict(self) -> dict:
        return {"type": "action_row", "items": [i.to_dict() for i in self.items]}


class ContainerSpoiler:
    def __init__(self, asset):
        self.asset = asset

    def to_dict(self) -> dict:
        return {"type": "spoiler", "asset": self.asset.to_dict()}


class Container:
    """.container[] — the top-level v2 embed wrapper holding any of the
    above component types in order."""

    def __init__(self):
        self.items: list = []

    def add(self, item) -> "Container":
        self.items.append(item)
        return self

    def to_dict(self) -> dict:
        return {"type": "container", "items": [i.to_dict() for i in self.items]}
