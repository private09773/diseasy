"""
diseasy/context.py (v0.2.3)

ctx.send auto-resolves <var> tokens in the message AND now in Embed
content (title, description, field names/values, footer) before
sending. Accepts a real Embed object (diseasy.Embed), converting it
to Discord's real embed JSON shape via .to_dict().
"""

from diseasy.runtime import resolve_vars
from .logger import log


def _resolve_embed(embed, ctx, local_vars) -> dict:
    """
    Resolves <var> tokens in every string field of an Embed before
    converting it to a plain dict for sending.
    """
    data = embed.to_dict()

    if "title" in data:
        data["title"] = resolve_vars(data["title"], ctx, local_vars)
    if "description" in data:
        data["description"] = resolve_vars(data["description"], ctx, local_vars)
    if "fields" in data:
        for field in data["fields"]:
            field["name"] = resolve_vars(field["name"], ctx, local_vars)
            field["value"] = resolve_vars(field["value"], ctx, local_vars)
    if "footer" in data and "text" in data["footer"]:
        data["footer"]["text"] = resolve_vars(data["footer"]["text"], ctx, local_vars)

    return data


class Context:
    def __init__(self, message, channel, author, guild, bot):
        self.message = message
        self.channel = channel
        self.author = author
        self.guild = guild
        self.bot = bot

    async def send(self, message: str = "", *, embed=None, view=None, ephemeral=False):
        """
        Sends a message to the channel this context belongs to.
        <var> tokens inside `message` AND inside `embed` (title,
        description, fields, footer) are resolved automatically.
        """
        local_vars = {
            "ctx": self,
            "member": getattr(self, "member", None),
            "author": self.author,
        }

        resolved_message = resolve_vars(message, self, local_vars) if message else message

        resolved_embed = None
        if embed is not None:
            if hasattr(embed, "to_dict"):
                resolved_embed = _resolve_embed(embed, self, local_vars)
            else:
                # Fallback: plain dict was passed directly (e.g. from
                # the parser's older __embed dict-guess) — send as-is.
                resolved_embed = embed

        if not resolved_message and not resolved_embed:
            log.warning("ctx.send called with no message or embed content")

        return await self.bot._http.send_message(
            channel_id=self.channel.id,
            content=resolved_message,
            embeds=[resolved_embed] if resolved_embed else None,
            components=view.to_payload() if view else None,
        )
