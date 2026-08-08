# This is an example main.py,
# you can remove this string if you
# want to. 
import diseasy

bot = diseasy.Bot(intents="intents", prefix="!")

@bot.event(name="on_ready")
async def on_ready():
    print("Bot is Online.")
    
bot.run("YOUR-TOKEN-HERE")    
