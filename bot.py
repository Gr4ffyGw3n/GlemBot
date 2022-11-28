import discord
import pafy
from discord.ext import commands
import validators
import vid
import asyncio
import socket
import urllib.parse
import random
import json
from datetime import datetime

print("bot.py loaded!")
class Player(commands.Cog):
    def __init__(self, bot_):
        self.bot = bot_
        self.song_que = {}
        self.current = {}
        self.current_time = {}
        self.server_settings = {}
        self.setup()
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
        self.perms = json.load(open('users.json'))
        print("bot.py finished init")

    def setup(self):
        for guild in self.bot.guilds:
            print(guild)
            self.song_que[guild.id]=[]
            self.server_settings[guild.id]={}
            self.server_settings[guild.id]['is_loop'] = False
            self.server_settings[guild.id]['index'] = 0
            self.server_settings[guild.id]['notify'] = True

    def check_perm(self, in_id):
        valid = False
        for id in self.perms["users_permitted"]:
            print("check " + str(id['ID']) + " with " + str(in_id))
            if int(in_id) == int(id['ID']):
                valid = True
        return valid
    async def to_msg(self, ctx, message):
        await ctx.send(f"```{message}```")
    async def check_queue(self, ctx):
        if len(self.song_que[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_que[ctx.guild.id][self.server_settings[ctx.guild.id]['index']])
            if self.server_settings[ctx.guild.id]['is_loop']:
                tmp_index = self.server_settings[ctx.guild.id]['index'] + 1
                self.server_settings[ctx.guild.id]['index'] += 1
                self.server_settings[ctx.guild.id]['index'] = tmp_index % len(self.song_que[ctx.guild.id])
            else:
                self.server_settings[ctx.guild.id]['index'] = 0
                self.song_que[ctx.guild.id].pop(0)

        else:
            self.current[ctx.guild.id] = None
            ctx.voice_client.stop()

    async def play_song(self, ctx, url):
        bot_client = ctx.voice_client
        song = pafy.new(url)
        self.current[ctx.guild.id] = song
        self.current_time[ctx.guild.id] = datetime.now()
        audio = song.getbestaudio()
        source = discord.FFmpegPCMAudio(audio.url, **self.FFMPEG_OPTIONS)

        bot_client.play(source, after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        bot_client.source = discord.PCMVolumeTransformer(bot_client.source,
                                                             volume=0.1)
        if self.server_settings[ctx.guild.id]['notify']:
            await ctx.send("Now Playing " + vid.vTitle(url) + "!")

    async def play_song2(self, ctx, url):
        bot_client = ctx.voice_client
        song = pafy.new(url)
        self.current[ctx.guild.id] = song
        self.current_time[ctx.guild.id] = datetime.now()
        audio = song.getbestaudio()
        source = discord.FFmpegudio(url, **self.FFMPEG_OPTIONS)

        bot_client.play(source, after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        bot_client.source = discord.PCMVolumeTransformer(bot_client.source,
                                                             volume=0.1)
        await ctx.send("Now Playing " + vid.vTitle(url) + "!")

    @commands.command(brief="joins the voice channel")
    async def join(self, ctx):
        print("trying to join")
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
        self.song_que[ctx.guild.id] = []
        await ctx.send("Goodbye!")

    @commands.command(brief="Plays songs from YouTube", aliases=['p'])
    async def play(self, ctx, *arg):
        song = "+".join(arg[:])
        print(song)
        is_url = validators.url(song)
        url = ""
        link = ""
        print(song)
        print(is_url)
        # Checks if input is an Url
        if is_url:
            link = song
            url = vid.toId(song)
        else:
            song = urllib.parse.quote(song)
            v_list = vid.ySearch(song)
            output = "Glemmy found these results"
            for i in range(len(v_list)):
                output += f"\n{str(i+1)}: {vid.vTitle(v_list[i])}"
            print(output)
            await self.to_msg(ctx, output)

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            selection = await self.bot.wait_for("message", check = check)
            print(v_list)
            url = v_list[int(selection.content)-1]
            link = vid.toLink(url)

        print(f"Url is {url} Link is {link}")

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_que[ctx.guild.id])
            if not ctx.voice_client.is_playing():
                await self.play_song(ctx, url)
            elif queue_len < 10:
                self.song_que[ctx.guild.id].append(url)
                print(f"added song {url} to que")
                print(f"here is the current que {self.song_que[ctx.guild.id]} to que")
                return await ctx.send(vid.vTitle(url) + f" has been added to the queue at position: {queue_len+1}.")
            else:
                return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")

        # await ctx.send(song)
        await self.play_song(ctx, url)

    @commands.command(brief="Displays the Queue", aliases = ['q'])
    async def queue(self, ctx):
        output = ""
        if self.current[ctx.guild.id] is not None:
            output += f"Currently playing {self.current[ctx.guild.id].title}\n"
        if len(self.song_que[ctx.guild.id]) == 0:
                output = output + ("Glemmy doesn't have anything in queue! ( ..•˘___˘• .. )")
        else:
            output = output + "Here is the current queue!\n"
            for i in range(len(self.song_que[ctx.guild.id])):
                output = output+f"{i+1}: "+vid.vTitle(self.song_que[ctx.guild.id][i])+"\n"
        await ctx.send("```" + output + f"\nLoop Queue: {self.server_settings[ctx.guild.id]['is_loop']}" + "```")

    @commands.command(brief="Completely kills the bot")
    async def die(self, ctx):
        if self.check_perm(ctx.message.author.id):
            await ctx.send("oof")
            exit()
        else:
            await ctx.send("Sorry, but you don't have the right permissions to kill Glemmy.")

    @commands.command()
    async def remove(self, ctx, arg):
        position = int(arg)-1
        current_pos = self.server_settings[ctx.guild.id]['index']
        try:
            self.song_que[ctx.guild.id].pop(position)
        except:
            output = "Index out of range or something else went wrong ;- ;;;"
        else:
            output = f"Track at position {position + 1} has been removed!"
            if current_pos <= position:
                self.server_settings[ctx.guild.id]['index'] = self.server_settings[ctx.guild.id]['index'] %\
                                                              len(self.song_que[ctx.guild.id])
        await ctx.send(output)
    @commands.command(brief="stops playing audio", aliases = ["s"])
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
        output = f"client_is_playing: {bot_client.is_playing()}\n" \
                 f"queue_looping: " \
                 f"{self.server_settings[ctx.guild.id]['is_loop']}\n" \
                 f"queue index: {self.server_settings[ctx.guild.id]['index']}\n" \
                 f"Notification on/off: {self.server_settings[ctx.guild.id]['notify']}"
        await ctx.send(f"```{output}```")

    @commands.command(brief="roll dice ~roll [how many] [what dice]")
    async def roll(self, ctx, *arg):
        num = int(arg[0])
        dtype = int(arg[1])
        out = "Glemmy rolled "
        out += "a " + "d" + str(dtype) + " " if num == 1 else str(num) + " d" + str(dtype) +"s "
        out += "and got \n"
        sum = 0
        for i in range(num):
            egg = random.randrange(1,dtype)
            out += str(egg) + " "
            sum += egg
        out += "\n for a total of " + str(sum)
        print(out)
        await ctx.send(out)

    @commands.command(brief="pause song")
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.send("Pausing!")

    @commands.command(brief="resume song", aliases = ["r"])
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.send("Resuming!")

    @commands.command(brief="resume song", aliases = ["c", "np"])
    async def current(self, ctx):
        output = ""
        current_t = (datetime.now()-self.current_time[ctx.guild.id]).seconds
        hour, remainder = divmod(current_t, 3600)
        minute, second = divmod(remainder, 60)
        if self.current[ctx.guild.id] is not None:
            output += f"Currently playing {self.current[ctx.guild.id].title} | "
            output += "{:02}:{:02}:{:02}".format(int(hour), int(minute), int(second)) + f" - {self.current[ctx.guild.id].duration}\n"
        else:
            output = "Glemmy isn't currently playing anything"
        await ctx.send(output)

    @commands.command(brief="loop queue", aliases = ["l"])
    async def loop(self, ctx):
        if self.server_settings[ctx.guild.id]['is_loop'] is False:
            self.server_settings[ctx.guild.id]['is_loop'] = True
            await ctx.send("Now looping queue!")
        else:
            self.server_settings[ctx.guild.id]['is_loop'] = False
            await ctx.send("No longer looping queue!")

    @commands.command(brief="clear queue")
    async def clear(self, ctx):
        self.song_que[ctx.guild.id] = []

    @commands.command(brief="clear queue")
    async def notif(self, ctx):
        self.server_settings[ctx.guild.id]['notify'] = not self.server_settings[ctx.guild.id]['notify']
        await self.to_msg(ctx, f"Notifications now set to: {self.server_settings[ctx.guild.id]['notify']}")