"""
diseasy/embed.py (v0.2.3)

Real Embed class for Embeds v1 (classic Discord embeds) — replaces
the parser's earlier __embed = {} dict-guess with an actual class
that matches Discord's real embed JSON schema, confirmed against
Discord's documented embed object shape:
  { title, description, color, fields: [{name, value, inline}],
    footer: {text}, thumbnail: {url}, image: {url} }

Maps to the notation:
    .embed[]
    .embedtitle("...")
    .embed_descriptor("...")
    .embedinline()          # marks the NEXT field as inline
    .embedasset.from[<.asset-embed>]

Usage in plain Python:
    from diseasy import Embed

    embed = Embed(title="Server Rules", description="Please read <guild.name>'s rules")
    embed.add_field(name="Rule 1", value="Be nice", inline=True)
    embed.set_footer("Requested by <user.name>")
    await ctx.send(message="Here are the rules:", embed=embed)
"""


class Embed:
    def __init__(self, title: str = None, description: str = None, color: int = None):
        self.title = title
        self.description = description
        self.color = color
        self.fields = []
        self.footer_text = None
        self.thumbnail_url = None
        self.image_url = None

    def add_field(self, name: str, value: str, inline: bool = False) -> "Embed":
        self.fields.append({"name": name, "value": value, "inline": inline})
        return self

    def set_footer(self, text: str) -> "Embed":
        self.footer_text = text
        return self

    def set_thumbnail(self, url: str) -> "Embed":
        self.thumbnail_url = url
        return self

    def set_image(self, url: str) -> "Embed":
        self.image_url = url
        return self

    def to_dict(self) -> dict:
        """
        Converts to Discord's real embed JSON shape. <var> tokens in
        title/description/field values/footer are NOT resolved here —
        resolution happens in ctx.send() via resolve_vars(), same as
        plain message text, so Embed stays a plain data class.
        """
        data = {}
        if self.title is not None:
            data["title"] = self.title
        if self.description is not None:
            data["description"] = self.description
        if self.color is not None:
            data["color"] = self.color
        if self.fields:
            data["fields"] = self.fields
        if self.footer_text is not None:
            data["footer"] = {"text": self.footer_text}
        if self.thumbnail_url is not None:
            data["thumbnail"] = {"url": self.thumbnail_url}
        if self.image_url is not None:
            data["image"] = {"url": self.image_url}
        return data
