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
import yt_dlp
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
        self.ydl_opts = {'format': 'bestaudio'}
        print("bot.py finished init")

    def setup(self):
        for guild in self.bot.guilds:
            print(guild)
            self.song_que[guild.id]=[]
            self.server_settings[guild.id]={}
            self.server_settings[guild.id]['is_loop'] = False
            self.server_settings[guild.id]['index'] = 0
            self.server_settings[guild.id]['cdur'] = 0
            self.server_settings[guild.id]['notify'] = True
            self.server_settings[guild.id]['embed'] = {}
            self.current[guild.id] = None

    def check_perm(self, in_id):
        valid = False
        for id in self.perms["users_permitted"]:
            print("check " + str(id['ID']) + " with " + str(in_id))
            if int(in_id) == int(id['ID']):
                valid = True
        return valid

    def to_msg(self, message):
        out = f"```{message}```"
        return out

    async def check_queue(self, ctx):
        if len(self.song_que[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_que[ctx.guild.id][0])
            # Song Removal
            if self.server_settings[ctx.guild.id]['is_loop']:
                self.song_que[ctx.guild.id].append(self.song_que[ctx.guild.id].pop(0))
            else:
                self.song_que[ctx.guild.id].pop(0)

        else:
            self.current[ctx.guild.id] = None
            ctx.voice_client.stop()

        await self.update_embed(ctx)

    def to_time(self, seconds):
        total = int(seconds)
        hour, remainder = divmod(total, 3600)
        minute, second = divmod(remainder, 60)
        return "[{:02}:{:02}:{:02}]".format(int(hour), int(minute), int(second))

    async def play_song(self, ctx, url):
        bot_client = ctx.voice_client
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            song = ydl.extract_info(url, download=False)
        self.current[ctx.guild.id] = url
        self.server_settings[ctx.guild.id]['cdur'] = song.get('duration')
        self.current_time[ctx.guild.id] = datetime.now()
        # audio = song.getbestaudio()
        source = discord.FFmpegPCMAudio(song["url"], **self.FFMPEG_OPTIONS)

        bot_client.play(source, after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        bot_client.source = discord.PCMVolumeTransformer(bot_client.source,
                                                         volume=0.1)
        #if self.server_settings[ctx.guild.id]['notify']:
        #    await ctx.send("Now Playing " + vid.vTitle(url) + "!")

    async def play_song2(self, ctx, url):
        bot_client = ctx.voice_client
        song = pafy.new(url)
        self.current[ctx.guild.id] = url
        self.current_time[ctx.guild.id] = datetime.now()
        audio = song.getbestaudio()
        source = discord.FFmpegudio(url, **self.FFMPEG_OPTIONS)

        bot_client.play(source, after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        await ctx.send("Now Playing " + vid.vTitle(url) + "!")

    def embed_handler(self, ctx):
        print("in the method lol")

        # Now playing field data handling
        c_title = vid.vTitle(self.current[ctx.guild.id]) if self.current[ctx.guild.id] else "None"
        c_time = self.to_time(self.server_settings[ctx.guild.id]['cdur'])
        print('NP field done')
        # Next up field data handling
        n_title = vid.vTitle(self.song_que[ctx.guild.id][0]) if self.song_que[ctx.guild.id] else "None"
        print('NU field done')
        embed = discord.Embed(title="Toast's Stage",
                              colour=0x00b0f4)

        embed.set_author(name="", url="https://example.com")

        embed.add_field(name="Now Playing", value=c_title, inline=True)
        embed.add_field(name="\u200B", value=f"{c_time}", inline=True)
        embed.add_field(name="\u200B", value="\u200B") # New Line
        embed.add_field(name="Next up", value=n_title, inline=True)
        embed.add_field(name="\u200B", value="\u200B", inline=True)

        embed.set_thumbnail(url="https://i.ibb.co/gjVfRx8/egg.png")
        return embed

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        for item in self.bot.voice_clients:
            if before.channel.id == item.channel.id:
                print(item.channel.members)
                print(len(item.channel.members))
                if len(item.channel.members) == 1:
                    print("someone disconnected")
                    await item.disconnect()
                    self.song_que[item.guild.id] = []
                    break

    @commands.command()
    async def update_embed(self, ctx):
        print('testing')
        print(self.server_settings[ctx.guild.id]['embed'])
        with open('guildsetting.json', 'r') as gs:
            jtmp = json.load(gs)
        print(jtmp)
        msg = await ctx.fetch_message(jtmp['embedmessage'][str(ctx.guild.id)])
        print(msg)
        await msg.edit(embed=self.embed_handler(ctx))

    @commands.command()
    async def makec(self, ctx):
        await ctx.send("Trying to write")
        out = {}
        out['outchannels'] = {}
        out['embedmessage'] = {}
        for guild in self.bot.guilds:
            out['outchannels'][str(guild.id)] = None
            out['embedmessage'][str(guild.id)] = None
        print(out)
        jsout = json.dumps(out, indent=4)
        with open("guildsetting.json", "w") as gs:
            gs.write(jsout)
        await ctx.send("Written")

    @commands.command()
    async def setc(self, ctx):
        await ctx.message.delete()
        print("starting")
        embed = self.embed_handler(ctx)
        print('embed generated')
        with open("guildsetting.json", "r") as gs:
            jtmp = json.load(gs)
        print(jtmp)
        msg = await ctx.send(embed=embed)
        jtmp['outchannels'][str(ctx.guild.id)] = ctx.channel.id
        jtmp['embedmessage'][str(ctx.guild.id)] = str(msg.id)
        print(f"The Jtmp To be out put {jtmp}")
        with open("guildsetting.json", "w") as gs:
            json.dump(jtmp, gs, indent=4)
        print(f'SetC Writing Complete')

    @commands.command(brief="joins the voice channel")
    async def join(self, ctx):
        await ctx.message.delete()
        print("trying to join")
        usr_client = ctx.author.voice
        bot_client = ctx.voice_client

        # checks if bot is already connected to a channel
        if bot_client is None:
            # await ctx.send("Joining " + str(usr_client.channel) + "!")
            await usr_client.channel.connect()

        # checks if user is connected to voice channel
        # elif usr_client is None:
            # await ctx.send("You must be connected to a voice channel!")

        # checks if bot is already connected to same channel as caller
        # elif bot_client.channel == usr_client.channel:
            # await ctx.send("I am already connected to the channel!")

        # checks if bot is connected to another channel as caller
        elif bot_client.channel != usr_client.channel:
            old_channel = str(ctx.voice_client.channel)
            await ctx.voice_client.disconnect()
            # await ctx.send("Leaving " + old_channel + " and joining " + str(usr_client.channel))
            await usr_client.channel.connect()
            return

    @commands.command(brief="Leaves vc")
    async def leave(self, ctx):
        await ctx.message.delete()
        await ctx.voice_client.disconnect()
        self.song_que[ctx.guild.id] = []
        self.server_settings[ctx.guild.id]['cdur'] = 0
        await self.update_embed(ctx)

    @commands.command()
    async def shutup(self, ctx):
        await ctx.send(f"{ctx.author.name}, you are stupid, eat piss.")
        await ctx.author.move_to(None)

    @commands.command(brief="Plays songs from YouTube", aliases=['p'])
    async def play(self, ctx, *arg):
        if ctx.voice_client is None:
            return
        content = arg[:]
        await ctx.message.delete()
        song = "+".join(content)
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
                time = self.to_time(v_list[i][1])
                output += f"\n{str(i+1)}: {time} {vid.vTitle(v_list[i][0])}"
            print(output)
            search_results = await ctx.send(self.to_msg(output))

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            selection = await self.bot.wait_for("message", check=check)
            print(f"selection type {type(selection)}")
            print(v_list)
            url = v_list[int(selection.content)-1][0]
            link = vid.toLink(url)
            await search_results.delete()
            await selection.delete()

        print(f"Url is {url} Link is {link}")

        if True:
            queue_len = len(self.song_que[ctx.guild.id])
            if queue_len < 20:
                self.song_que[ctx.guild.id].append(url)
                print(f"added song {url} to que")
                print(f"here is the current que {self.song_que[ctx.guild.id]} to queue")
                await self.update_embed(ctx)
                # await ctx.send(vid.vTitle(url) + f" has been added to the queue at position: {queue_len+1}.")
            #else:
                # return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")
            if not ctx.voice_client.is_playing():
                await self.check_queue(ctx)


    @commands.command(brief="Displays the Queue", aliases = ['q'])
    async def queue(self, ctx):
        output = ""
        if self.current[ctx.guild.id] is not None:
            output += f"Currently playing {vid.vTitle(self.current[ctx.guild.id])}\n"
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

    @commands.command(brief="Swap the position between songs")
    async def swap(self, ctx, *args):
        pos = []
        output = ""
        for item in args:
            pos.append(int(item)-1)
        print(pos)
        try:
            self.song_que[ctx.guild.id][pos[0]], self.song_que[ctx.guild.id][pos[1]] = self.song_que[ctx.guild.id][pos[1]], \
                                                                         self.song_que[ctx.guild.id][pos[0]]
        except:
            output = "Something went wrong ;- ;;;"
        else:
            output = f"Tack {pos[0]+1} has been swapped with Track {pos[1]+1}!"

        await ctx.send(output)

    @commands.command(brief = "Move the selected track to the desired position", aliases = ['m'])
    async def move(self, ctx, *args):
        pos = []
        queue = self.song_que[ctx.guild.id]
        for item in args:
            pos.append(int(item)-1)
        tmp = self.song_que[ctx.guild.id].pop(pos[0])
        self.song_que[ctx.guild.id].insert(pos[1],tmp)

        await ctx.send(f"Tack {pos[0]+1} has been moved to position {pos[1]+1}!")

    @commands.command(brief="Brings selected song to top of queue", aliases = ["t"])
    async def top(self, ctx, arg):
        pos = int(arg)-1
        tmp = self.song_que[ctx.guild.id].pop(pos)
        self.song_que[ctx.guild.id].insert(0, tmp)

    @commands.command()
    async def qfill(self, ctx):
        self.song_que[ctx.guild.id].extend(['F9z9D30rESA','8jFio-603hY'])

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
        await ctx.message.delete()
        bot_client = ctx.voice_client

        if bot_client is None:
            # await ctx.send("I'm not connected to any channels!")
            return
        elif bot_client.is_playing():
            # await ctx.send("Skipping!")
            bot_client.stop()
        else:
            # await ctx.send("I'm not playing anything!")
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
        await ctx.send("Queue has been cleared!")

    @commands.command(brief="toggles notification for when a new song is played")
    async def notif(self, ctx):
        self.server_settings[ctx.guild.id]['notify'] = not self.server_settings[ctx.guild.id]['notify']
        await self.to_msg(ctx, f"Notifications now set to: {self.server_settings[ctx.guild.id]['notify']}")
