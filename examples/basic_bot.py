"""A minimal Diseasy bot: connects and responds to a raw on_message event."""
import diseasy

client = diseasy.Client(intents=["guilds", "messages", "message_content"])


@client.event(name="on_ready")
async def on_ready():
    print("Diseasy is ready.")


@client.event(name="on_message")
async def on_message(message):
    if message.content == "!ping":
        await message.channel.send("Pong!")


client.run("YOUR_TOKEN_HERE")
