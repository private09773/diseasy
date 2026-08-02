"""Assets: .asset-embed / .asset-noembed / .asset-getfrom"""


class AssetEmbed:
    """.asset-embed[source="example.jpg"] — shows the asset inline in the message."""

    def __init__(self, source: str):
        self.source = source
        self.embed = True

    def to_dict(self) -> dict:
        return {"source": self.source, "embed": True}


class AssetNoEmbed:
    """.asset-noembed[source="example.jpg"] — attaches the asset without an inline preview."""

    def __init__(self, source: str):
        self.source = source
        self.embed = False

    def to_dict(self) -> dict:
        return {"source": self.source, "embed": False}


class AssetGetFrom:
    """.asset-getfrom[internet=true/false, source="example.com"] — fetches an
    asset either from the web or from local/attachment storage."""

    def __init__(self, source: str, internet: bool = False):
        self.source = source
        self.internet = internet

    def to_dict(self) -> dict:
        return {"source": self.source, "internet": self.internet}
