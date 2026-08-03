"""
diseasy/context.py (v0.1.1a)

ctx.send now takes message as a keyword, matching the message=f""
call style rather than a positional string. This is a breaking
change from prior versions where ctx.send("text") was positional.

NOTE: I don't have your actual Context/HTTP-sending class, so this
is a standalone reference implementation. Merge the send() method
below into your real class rather than replacing the whole file —
your real version almost certainly also handles embeds, files,
components, etc. that aren't reproduced here.
"""

from .logger import log


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

        Old style (v0.1.1 and earlier):
            await ctx.send("Hello!")

        New style (v0.1.1a):
            await ctx.send(message=f"Hello {ctx.author.name}!")

        Both still work here since `message` accepts a positional or
        keyword string — but going forward, examples/docs should use
        the message=f"" form for clarity, matching the rest of the
        notation's explicitness.
        """
        if not message and not embed:
            log.warning("ctx.send called with no message or embed content")

        payload = {"content": message}
        if embed is not None:
            payload["embed"] = embed
        if view is not None:
            payload["components"] = view.to_payload()

        return await self.bot.http.send_message(
            channel_id=self.channel.id,
            payload=payload,
            ephemeral=ephemeral,
        )
