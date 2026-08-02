"""A bot using a slash command with an option, via <option.from""> access."""
import diseasy
from diseasy.ext.slash import slash_command, sync_commands

client = diseasy.Client(intents=["guilds"])


@slash_command(name="greet", description="Greet someone by name")
async def greet(interaction):
    name = interaction.option_from("name")
    await interaction.send(f"Hello, {name}!")


greet.slashoption("name", type="str", required=True, description="Who to greet")


async def setup():
    await sync_commands(client, application_id=123456789012345678, commands=[greet])


client.run("YOUR_TOKEN_HERE")
