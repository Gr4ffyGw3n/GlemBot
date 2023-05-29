import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from bot import Player

load_dotenv()
intents = discord.Intents.default()
intents.messages = True
intents.members = True
bot = commands.Bot(command_prefix='=', intents=discord.Intents.all())

TOKEN = os.getenv('DISCORD_TOKEN')


@bot.event
async def on_ready():
    print("Glemmy is ready!")


async def setup():
    await bot.wait_until_ready()
    await bot.add_cog(Player(bot))


async def main():
    async with bot:
        bot.loop.create_task(setup())
        await bot.start(TOKEN)
print(TOKEN)
# bot.run(TOKEN)
asyncio.run(main())
