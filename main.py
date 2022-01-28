import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from bot import Player

load_dotenv()
bot = commands.Bot(command_prefix='~')

TOKEN = os.getenv('DISCORD_TOKEN')


@bot.event
async def on_ready():
    print("Glemmy is ready!")


async def setup():
    await bot.wait_until_ready()
    bot.add_cog(Player(bot))

bot.loop.create_task(setup())
bot.run(TOKEN)

