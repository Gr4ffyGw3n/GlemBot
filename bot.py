import discord
import pafy
from discord.ext import commands
import validators
import vid
import asyncio
import youtube_dl
import socket
import urllib.parse

class Player(commands.Cog):
    def __init__(self, bot_):
        self.bot = bot_
        self.song_que = {}

        self.setup()
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

    def setup(self):
        for guild in self.bot.guilds:
            self.song_que[guild.id]=[]

    async def check_queue(self, ctx):
        if len(self.song_que[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_que[ctx.guild.id][0])
            self.song_que[ctx.guild.id].pop(0)

    async def play_song(self, ctx, url):
        bot_client = ctx.voice_client
        song = pafy.new(url)
        audio = song.getbestaudio()
        source = discord.FFmpegPCMAudio(audio.url, **self.FFMPEG_OPTIONS)

        bot_client.play(source, after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        bot_client.source = discord.PCMVolumeTransformer(bot_client.source,
                                                             volume=0.1)
        await ctx.send("Now Playing " + vid.vTitle(url) + "!")

    @commands.command(brief="joins the voice channel")
    async def join(self, ctx):
        usr_client = ctx.author.voice
        bot_client = ctx.voice_client

        # checks if bot is already connected to a channel
        if bot_client is None:
            await ctx.send("Joining " + str(usr_client.channel) + "!")
            await usr_client.channel.connect()

        # checks if user is connected to voice channel
        elif usr_client is None:
            await ctx.send("You must be connected to a voice channel!")

        # checks if bot is already connected to same channel as caller
        elif bot_client.channel == usr_client.channel:
            await ctx.send("I am already connected to the channel!")

        # checks if bot is connected to another channel as caller
        elif bot_client.channel != usr_client.channel:
            old_channel = str(ctx.voice_client.channel)
            await ctx.voice_client.disconnect()
            await ctx.send("Leaving " + old_channel + " and joining " + str(usr_client.channel))
            await usr_client.channel.connect()
            return

    @commands.command(brief="Leaves vc")
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.send("Goodbye!")

    @commands.command(brief="Plays songs from YouTube")
    async def play(self, ctx, *arg):
        song = "+".join(arg[:])
        song = urllib.parse.quote(song)
        is_url = validators.url(song)

        # Checks if input is an Url
        if is_url:
            url = song
        else:
            url = vid.ySearch(song)

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_que[ctx.guild.id])
            if not ctx.voice_client.is_playing():
                await self.play_song(ctx, url)
            elif queue_len < 10:
                self.song_que[ctx.guild.id].append(url)
                return await ctx.send(vid.vTitle(url) + f" has been added to the queue at position: {queue_len+1}.")
            else:
                return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")

        # await ctx.send(song)
        await self.play_song(ctx, url)

    @commands.command(brief="Displays the Queue")
    async def queue(self, ctx):
        output="Here is the current queue!\n"
        if len(self.song_que[ctx.guild.id]) == 0:
            await ctx.send("Glemmy doesn't have anything in queue! ( ..•˘___˘• .. )")
            await ctx.send("So eat my ass sideways and die")
        else:
            for i in range(len(self.song_que[ctx.guild.id])):
                output = output+f"{i+1}: "+vid.vTitle(self.song_que[ctx.guild.id][i])+"\n"
            await ctx.send(output)

    @commands.command(brief="Completely kills the bot")
    async def die(self, ctx):
        await ctx.send("oof")
        exit()

    @commands.command()
    async def remove(self,ctx, pos):
        position = int(pos)-1
        await ctx.send(vid.vTitle(self.song_que[ctx.guild.id][position])+"has been removed!")
        self.song_que[ctx.guild.id].pop(position)

    @commands.command(brief="stops playing audio")
    async def skip(self, ctx):
        bot_client = ctx.voice_client

        if bot_client is None:
            await ctx.send("I'm not connected to any channels!")
        elif bot_client.is_playing():
            await ctx.send("Skipping!")
            bot_client.stop()
        else:
            await ctx.send("I'm not playing anything!")
            return

    @commands.command(brief="stops playing audio")
    async def status(self, ctx):
        bot_client = ctx.voice_client
        await ctx.send(bot_client.is_playing())
