# This is an example main.py with prefix commands,
# you can remove this string if you
# want to. 
import diseasy
from diseasy.ext.commands import command

bot = diseasy.Bot(intents="intents", prefix="!")

@bot.event(name="on_ready")
async def on_ready():
    print("Bot is Online.")
    
# Command's.
@command(name="ping", description="Pong!")
async def ping(self, ctx):
    await ctx.send(message="Pong!")
# Add as many as you like.
    
bot.run("YOUR-TOKEN-HERE")    
