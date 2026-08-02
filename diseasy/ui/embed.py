"""Embeds v1 — the classic embed: .embed[], .embedtitle(), .embed_descriptor(),
.embedinline(), .embedasset.from[<.asset-embed>]"""


class Embed:
    def __init__(self, *, color: int | None = None):
        self.title: str | None = None
        self.description: str | None = None
        self.color = color
        self.fields: list[dict] = []
        self.asset: dict | None = None

    def embedtitle(self, text: str) -> "Embed":
        self.title = text
        return self

    def embed_descriptor(self, text: str) -> "Embed":
        self.description = text
        return self

    def embedinline(self, name: str, value: str, inline: bool = True) -> "Embed":
        self.fields.append({"name": name, "value": value, "inline": inline})
        return self

    def embedasset_from(self, asset) -> "Embed":
        """.embedasset.from[<.asset-embed>] — attach an AssetEmbed as the
        embed's image."""
        self.asset = asset.to_dict()
        return self

    def to_dict(self) -> dict:
        data: dict = {}
        if self.title:
            data["title"] = self.title
        if self.description:
            data["description"] = self.description
        if self.color is not None:
            data["color"] = self.color
        if self.fields:
            data["fields"] = self.fields
        if self.asset:
            data["image"] = {"url": self.asset["source"]}
        return data
