import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from bot import Player

load_dotenv()
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='=', intent=intents)

TOKEN = os.getenv('DISCORD_TOKEN')


@bot.event
async def on_ready():
    print("Glemmy is ready!")


async def setup():
    await bot.wait_until_ready()
    bot.add_cog(Player(bot))

print(TOKEN)
bot.loop.create_task(setup())
bot.run(TOKEN)

