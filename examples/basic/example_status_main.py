# This is an example main.py with status,
# you can remove this string if you
# want to. 
import diseasy
from diseasy import playing, watching, listening, custom_status

bot = diseasy.Bot(intents="intents", prefix="!")

@bot.event(name="on_ready")
async def on_ready():
    await bot.set_presence(playing("with Diseasy")) # You can configure the text or status if you like.
    # or await bot.set_presence(watching("with Diseasy"))
    # or await bot.set_presence(listening("with Diseasy"))
    # or await bot.set_presence(custom_status("Hi!"))
    print("Bot is Online.")
    
bot.run("YOUR-TOKEN-HERE")    
