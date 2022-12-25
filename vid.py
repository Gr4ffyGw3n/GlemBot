import pafy
import os
import urllib.request
import urllib
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
import json
import isodate
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
import requests
import youtube_dl as ydl

load_dotenv()
api_key = os.getenv('GOOGLE_API')
pafy.set_api_key(api_key)

service = build('youtube', 'v3', developerKey=api_key)
class Queue():
    def __init__(self, bot):
        self.bot = bot
        self.song_que = {}

    async def pop_queue(self, ctx):
        if len(self.song_que[ctx.guild.id]) > 0:
            self.song_que[ctx.guild.id].pop(0)

    async def add_song(self, ctx, url):
        self.song_que[ctx.guild.id].append(url)

    async def return_song(self, ctx):
        return self.song_que[ctx.guild.id][0]

def toLink(id):
    return "https://www.youtube.com/watch?v=" + str(id)

def toId(url):
    return re.findall(r"watch\?v=(\S{11})", url)[0]

def ySearch(keyword: str):
    search_keyword=keyword
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
    #Getting Vid Duration
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    video_ids = list(dict.fromkeys(video_ids))
    song_lists = []
    for i in range (5):
        searchUrl = "https://www.googleapis.com/youtube/v3/videos?id=" + video_ids[i] + "&key=" + api_key + "&part=contentDetails"
        response = urllib.request.urlopen(searchUrl).read()
        data = json.loads(response)
        all_data = data['items']
        contentDetails = all_data[0]['contentDetails']
        duration = isodate.parse_duration(contentDetails['duration']).total_seconds()
        song_lists.append([video_ids[i], duration])
    print(song_lists)
    return song_lists

def vTitle(url):
    print(url)
    request = service.videos().list(
        part = "snippet",
        id = url
    )
    response = request.execute()
    print(response['items'][0]['snippet']['title'])
    return response['items'][0]['snippet']['title']

def getSource(url):
    song = pafy.new(url)
    audio = song.getbestaudio()
    return audio

def getSource(url):
    song = pafy.new(url)
    audio = song.getbestaudio()
    return audio
