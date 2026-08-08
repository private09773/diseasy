# This is an example main.py with cogs,
# you can remove this string if you
# want to. 
import diseasy

bot = diseasy.Bot(intents="intents", prefix="!")

# Load how many cogs you want.
cogs = {
   "cogs.utils", # Note: You can set how many cogs you like.
   }
   
@bot.event(name="on_ready")
async def on_ready():
    print("Bot is Online.")
    
bot.run("YOUR-TOKEN-HERE")    
