"""A cog bundling a command and an event, using the {} container."""
import diseasy
from diseasy.ext.commands import Cog, command


class Greetings(Cog):
    @command(name="hello", description="Say hello")
    async def hello(self, ctx):
        await ctx.respond("Hello there!")

    async def cog_check(self, ctx) -> bool:
        return True


client = diseasy.Client(intents=["guilds", "messages"])
client.add_cog = lambda cog_cls: cog_cls()  # placeholder wiring for the example
client.add_cog(Greetings)

client.run("YOUR_TOKEN_HERE")
