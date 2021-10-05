import discord
from discord.ext import commands
from discord.gateway import DiscordClientWebSocketResponse
from youtube_dl import YoutubeDL
import time
import asyncio
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from urllib.parse import quote_plus

import os

import random

command_prefix = '.'
bot = commands.Bot(command_prefix = command_prefix)
client = discord.Client()


# 음악 목록
music_user = []
music_title = []
music_queue = []
music_now = []
music_thumbnail = []



# Event 디스코드 시작
@bot.event
async def on_ready():
    await bot.change_presence(status = discord.Status.online, activity = discord.Game('XX'))

    print('Logging')
    print(bot.user.name)
    print('TOKEN =', TOKEN)
    print('Successly access')

    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')


        

# f_music_title 함수
@bot.command()
async def f_music_title(ctx, msg):
    global Text

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver = load_chrome_driver()

    try:
        driver.get("https://www.youtube.com/results?search_query="+msg)
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        
    except:
        if "https://www.youtube.com/watch?v=" in msg:
            msg = msg[32:]
        elif "https://youtu.be/" in msg:
            msg = msg[17:]
        driver.get("https://www.youtube.com/results?search_query="+msg)
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]

    music = entireNum.text.strip()

    music_title.append(music)
    music_now.append(music)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com'+test1
        
    #썸네일
    test1_video_number = test1[9:]
    test1_thumbnail = 'http://img.youtube.com/vi/'+ test1_video_number +'/0.jpg'
    music_thumbnail.append(test1_thumbnail)

    with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']

    
    return music, URL

# music_play 함수
@bot.command()
async music_play(ctx):
    global vc
    
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    URL = music_queue[0]
    del music_user[0]
    del music_title[0]
    del music_queue[0]
    del music_thumbnail[0]
    
    vc = get(bot.voice_clients, guild = ctx.guild)
    
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: music_play_next(ctx)) 

# music_play_next 함수
@bot.command()
async music_play_next(ctx):
    global music_msg
    if len(music_now) - len(music_user) >= 2:
        for i in range(len(music_now) - len(music_user) - 1):
            del music_now[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(music_user) >= 1:
        if not vc.is_playing():
            del music_now[0]
            URL = music_queue[0]
            del music_user[0]
            del music_title[0]
            del music_queue[0]
            del music_thumbnail[0]
            
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: music_play_next(ctx))

            try:
                musicmessage(bot)
            except:
                pass


    else:
        if not vc.is_playing():
            try:
                ex = len(music_now) - len(music_user)
                del music_user[:]
                del music_title[:]
                del music_queue[:]
                del music_thumbnail[:]
                while True:
                    try:
                        del music_now[ex]
                    except:
                        break
            except:
                pass
            


# 구글 드라이버 세팅 함수
def load_chrome_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    return webdriver.Chrome(executable_path=str(os.environ.get('CHROME_EXECUTABLE_PATH')), chrome_options=options)


# Command /도움말
@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(title = "인정봇", description = "")
    embed.set_author(name = "ㅇㅈ#6079", icon_url = 'https://cdn.discordapp.com/avatars/270403684389748736/621692a4dddbf42dd2b01df1301eebe6.png')
    embed.add_field(name = "명령어", value = ".join .leave .play (노래제목) .queuedel (숫자) .queue .queueclear \n"
                                            + ".musicinfo .pause .resume .skip .stop .음악메세지생성 .musicmessage \n"
                                            + ".메세지생성 (명령어) (메세지) .메세지삭제 (명령어) .메세지리스트 \n"
                                            + ".타겟메세지생성 (@호출) (명령어) (메세지) .타겟메세지삭제 (명령어) .타겟메세지리스트", inline = False)
    await ctx.send(embed=embed)


# Command /join
@bot.command()
async def join(ctx):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 입장해 주세요")


# Command /leave
@bot.command()
async def leave(ctx):
    try:
        client.loop.create_task(vc.disconnect())
    except:
        await ctx.send("인정봇이 음성 채널에 들어가 있지 않네요")


# Command /URLplay url
@bot.command()
async def URLplay(ctx, *, url):
    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    else:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        #music_user.append(msg)
        #result, URLTEST = f_music_title(msg)
        #music_queue.append(URLTEST)

# Command /play 노래제목
@bot.command()
async def play(ctx, *, msg):
    global vc
    try:
        await join(ctx)
    except:
        pass
    
    if not vc.is_playing():
        global entireText
        options = webdriver.ChromeOptions()
        options.add_argument("headless")


        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        driver = load_chrome_driver()

        try:
            driver.get("https://www.youtube.com/results?search_query="+msg)
            source = driver.page_source
            bs = bs4.BeautifulSoup(source, 'lxml')
            entire = bs.find_all('a', {'id': 'video-title'})
            entireNum = entire[0]

            
        except:
            if "https://www.youtube.com/watch?v=" in msg:
                msg = msg[32:]
            elif "https://youtu.be/" in msg:
                msg = msg[17:]
            driver.get("https://www.youtube.com/results?search_query="+msg)
            source = driver.page_source
            bs = bs4.BeautifulSoup(source, 'lxml')
            entire = bs.find_all('a', {'id': 'video-title'})
            entireNum = entire[0]

        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl

        video_number = musicurl[9:]
        image_type = '0'
        thumbnail = 'http://img.youtube.com/vi/'+ video_number +'/'+ image_type +'.jpg'

            
        music_now.insert(0, entireText)
        music_thumbnail.insert(0, thumbnail)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: music_play_next(ctx))

    else:
        music_user.append(msg)
        result, URLTEST = f_music_title(msg)
        music_queue.append(URLTEST)


# Command /queuedel (숫자)
@bot.command()
async def queuedel(ctx, *, number):
    try:
        ex = len(music_now) - len(music_user)
        del music_user[int(number) - 1]
        del music_title[int(number) - 1]
        del music_queue[int(number)-1]
        del music_now[int(number)-1+ex]
        del music_thumbnail[int(number)-1+ex]
            
        await ctx.send("대기열이 정상적으로 삭제되었습니다")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없네요")
            
        elif len(list) < int(number):
            await ctx.send("목록의 개수는 " + str(len(list)) + "이에요")
            
        else:
            await ctx.send("숫자를 입력해주세요!")

# Command /queue
@bot.command()
async def queue(ctx):
    if len(music_title) == 0:
        await ctx.send("노래를 등록해주세요")
    else:
        global Text
        Text = ""
        for i in range(len(music_title)):
            Text = Text + "\n" + str(i + 1) + ". " + str(music_title[i])
            
        await ctx.send(embed = discord.Embed(title = "노래목록", description = Text.strip()))


# Command /queueclear
@bot.command()
async def queueclear(ctx):
    try:
        ex = len(music_now) - len(music_user)
        del music_user[:]
        del music_title[:]
        del music_queue[:]
        del music_thumbnail[:]
        while True:
            try:
                del music_now[ex]
            except:
                break
        await ctx.send("목록이 초기화 되었습니다")
    except:
        await ctx.send("노래를 등록해주세요")


            
# Command /musicinfo
@bot.command()
async def musicinfo(ctx):
    if not vc.is_playing():
        await ctx.send("노래를 재생하고 있지 않네요")
    else:
        await ctx.send("현재 " + music_now[0] + "을(를) 재생하고 있습니다")


# Command /pause
@bot.command()
async def pause(ctx):
    try:
        vc.pause()
    except:
        await ctx.send("노래를 재생하고 있지 않네요")


# Command /resume
@bot.command()
async def resume(ctx):
    try:
        vc.resume()
    except:
         await ctx.send("노래를 재생하고 있지 않네요")

# Command /skip
@bot.command()
async def skip(ctx):
    if vc.is_playing():
        if len(music_user) >= 1:
            vc.stop()

        else:
            await ctx.send("스킵할 노래가 없네요")
    else:
        await ctx.send("노래를 재생하고 있지 않네요")

# Command /stop
@bot.command()
async def stop(ctx):
    if vc.is_playing():
        vc.stop()
    else:
        await ctx.send("노래를 재생하고 있지 않네요")
    try:
        ex = len(music_now) - len(music_user)
        del music_user[:]
        del music_title[:]
        del music_queue[:]
        del music_thumbnail[:]
        while True:
            try:
                del music_now[ex]
            except:
                break
    except:
        pass
        
    try:
        client.loop.create_task(vc.disconnect())
    except:
        pass


# 봇 전용 음악 채널 만들기
@bot.command(pass_context = True)
async def 음악메세지생성(ctx):
    global music_msg

    embed = discord.Embed(title='인정 Music', description='')
    embed.set_image(url = 'https://i.ytimg.com/vi/1SLr62VBBjw/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCbXp098HNZl_SbZ5Io5GuHd6M4CA')
                                   
    music_msg = await ctx.send('노래 목록 \n', embed=embed)

    music_reaction_list = ['✅','▶','⏸','⏹','⏭']
    for n in music_reaction_list:
        await music_msg.add_reaction(n)


@bot.command(pass_context = True)
async def musicmessage(ctx):
    text = []
    for i in range(len(music_title)):
        text.append('' + "\n" + str(i + 1) + ". " + str(music_title[i]))
    text.reverse()
    Text = ''
    for i in range(len(text)):
        Text = Text + str(text[i])

    try:
        global music_msg

        await music_msg.edit(content = '노래 목록 \n' + Text.strip())
        
        try:
            embed_music = discord.Embed(title='인정 Music \n' + music_now[0], description='')
            embed_music.set_image(url=music_thumbnail[0])
            await music_msg.edit(embed=embed_music)
        except:
            pass
            

        if not vc.is_playing():
            embed_music_f = discord.Embed(title='인정 Music', description='')
            embed_music_f.set_image(url='https://i.ytimg.com/vi/1SLr62VBBjw/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCbXp098HNZl_SbZ5Io5GuHd6M4CA')
            await music_msg.edit(embed=embed_music_f)

    except:
        embed_music = discord.Embed(title='인정 Music \n' + music_now[0], description='')
        embed_music.set_image(url=music_thumbnail[0])
        await ctx.send(embed=embed_music)

# 봇 전용 음악 채널 버튼 만들기
@bot.event
async def on_reaction_add(reaction, ctx):
    global vc

    if (reaction.emoji == '✅'):
        await musicmessage(bot)

    if (reaction.emoji == '▶' ):
        try:
            vc.resume()
        except:
            pass

    if (reaction.emoji == '⏸'):
        try:
            vc.pause()
        except:
            pass

    if (reaction.emoji == '⏹'):
        if vc.is_playing():
            try:
                vc.stop()
            except:
                pass
            try:
                ex = len(music_now) - len(music_user)
                del music_user[:]
                del music_title[:]
                del music_queue[:]
                del music_thumbnail[:]
                while True:
                    try:
                        del music_now[ex]
                    except:
                        break
            except:
                pass
            
            time.sleep(0.01)
            await musicmessage(bot)

    if (reaction.emoji == '⏭'):
        if vc.is_playing():
            if len(music_user) >= 1:
                vc.stop()

            time.sleep(0.01)    
            await musicmessage(bot)
            


talk = {'하앙': '하앍', '루이야오늘괜찮아?': '오빠 오늘 안전한 날이야', '루이야': '뭐 씹덕아;;', '날경멸해줘': '오타쿠 같은 새끼 죽어', '으흣..!': '죽어버렷!!', '루이야좋아해': '그럼 언니는 어쩌고..', '그치만니가더좋아': '으흣..나도널좋아해', '루이야..날매도해줘': '바보..! 변태..! 치한..!', '루이야좋아?': '으..응 으흣!!!', '어때좋았어?': '응 니가 제일 잘해', '루이야처음이야?': '아니 그날 너랑한게 처음이야..', '그럼이제두번째네?': '응.. 맞아..', '루이야오늘어때?': '나 오늘 그날이야'}


@bot.command()
async def 메세지생성(ctx, msg1, *, msg2):
    talk[msg1] = msg2
    await ctx.send(f'```명령어이름: {msg1}, 대답: {msg2} (이)가 등록되었습니다.```')

@bot.command()
async def 메세지삭제(ctx, msg1):
    del talk[msg1]
    await ctx.send(f'```명령어이름: {msg1} (이)가 삭제되었습니다.```')

@bot.command()
async def 메세지리스트(ctx):
    await ctx.send(f'```{talk}```')

@bot.command()
async def 로또(ctx, number=1):
    for i in range(number):
        lotto = random.sample(range(1,46),6)
        await ctx.send(f'```{lotto}```')



@bot.event
async def on_message(msg):
    global vc
    topic = msg.channel.topic

    if msg.author.id == 887582865762689035:
        return None

    if msg.content[:1] == command_prefix:
        await bot.process_commands(msg)

    else:
        if topic != None and '#인정_Music' in topic:
            try:
                vc = await msg.author.voice.channel.connect()
            except:
                pass
            
            
            await play(bot, msg=msg.content)

            await msg.delete()
            await musicmessage(bot)


        elif topic != None and '#대화' in topic:
            if msg.content in list(talk.keys()):
                await msg.channel.send(talk[msg.content])
        
            
                
                
TOKEN = os.environ['BOT_TOKEN']
bot.run(TOKEN)
