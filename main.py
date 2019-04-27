import discord
from discord.ext import commands
import asyncio
import os
import time
import youtube_dl
import inspect
import datetime
from discord import opus

# You will need to install FFMPEG for this to work
# If you don't know what to do get help a friend from the bot server!

#-------#
# STEPS #
#-------#

# Paste this near / at the top
# Change the prefix if needed
# if this is going to be your main code paste your token at bottom
# Change the prints if needed
# Run this code
# Any errors occur dm Steveo
# Code made by Steveo#5019

start_time = time.time()

client = commands.Bot(command_prefix=("-")) # <--- change prefix if needed
songs = asyncio.Queue()
play_next_song = asyncio.Event()
client.remove_command("help")

players = {}
queues = {}

def check_queue(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()

@client.event 
async def on_ready():
    await client.change_presence(game=discord.Game(name="Music | -help"), status=discord.Status("idle"))
    print('Logged in as')
    print("User name:", client.user.name) # <----- Change the prints if needed
    print("User id:", client.user.id)
    
async def audio_player_task():
    while True:
        play_next_song.clear()
        current = await songs.get()
        current.start()
        await play_next_song.wait()


def toggle_next():
    client.loop.call_soon_threadsafe(play_next_song.set)


@client.command(pass_context=True)
async def plays(ctx, url):
    # Shows how many plays the video has
    if not client.is_voice_connected(ctx.message.server):
        voice = await client.join_voice_channel(ctx.message.author.voice_channel)
    else:
        voice = client.voice_client_in(ctx.message.server)
        
        player = await voice.create_ytdl_player(url, after=toggle_next)
        await songs.put(player)
    

@client.command(name="join", pass_context=True, no_pm=True)
async def _join(ctx):
    # Joins the voice channel
    user = ctx.message.author
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Successfully connected to voice channel:", value=channel)
    await client.say(embed=embed)
    
@client.command(name="leave", pass_context=True, no_pm=True)
async def _leave(ctx):
    # Leaves the voice channel
    user = ctx.message.author
    server = ctx.message.server
    channel = ctx.message.author.voice.voice_channel
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Successfully disconnected from:", value=channel)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def pause(ctx):
    # Pauses the current video
    user = ctx.message.author
    id = ctx.message.server.id
    players[id].pause()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Player Paused", value=f"Requested by {ctx.message.author.name}")
    await client.say(embed=embed)

@client.command(pass_context=True)
async def skip(ctx):
    # Skips the video to the next queued
    user = ctx.message.author
    id = ctx.message.server.id
    players[id].stop()
    embed = discord.Embed(colour=user.colour)
    embed.add_field(name="Player Skipped", value=f"Requested by {ctx.message.author.name}")
    await client.say(embed=embed)

@client.command(name="play", pass_context=True)
async def _play(ctx, *, name):
    # Plays the video requested
    author = ctx.message.author
    name = ctx.message.content.replace("-play ", '')
    fullcontent = ('http://www.youtube.com/results?search_query=' + name)
    text = requests.get(fullcontent).text
    soup = bs4.BeautifulSoup(text, 'html.parser')
    img = soup.find_all('img')
    div = [ d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']]
    a = [ x for x in div[0].find_all('a') if x.has_attr('title') ]
    title = (a[0]['title'])
    a0 = [ x for x in div[0].find_all('a') if x.has_attr('title') ][0]
    url = ('http://www.youtube.com'+a0['href'])
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
    players[server.id] = player
    print("User: {} From Server: {} is playing {}".format(author, server, title))
    player.start()
    embed = discord.Embed(description="**__Song Play By MUZICAL STEVEO__**")
    embed.set_thumbnail(url="https://i.pinimg.com/originals/03/2b/08/032b0870b9053a191b67dc8c3f340345.gif")
    embed.add_field(name="Now Playing", value=title)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def queue(ctx, *, name):
    # Queue a video to play
    name = ctx.message.content.replace("m.queue ", '')
    fullcontent = ('http://www.youtube.com/results?search_query=' + name)
    text = requests.get(fullcontent).text
    soup = bs4.BeautifulSoup(text, 'html.parser')
    img = soup.find_all('img')
    div = [ d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']]
    a = [ x for x in div[0].find_all('a') if x.has_attr('title') ]
    title = (a[0]['title'])
    a0 = [ x for x in div[0].find_all('a') if x.has_attr('title') ][0]
    url = ('http://www.youtube.com'+a0['href'])
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
    
    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
    embed = discord.Embed(description="**__Song Play By STEVEO__**")
    embed.add_field(name="Video queued", value=title)
    await client.say(embed=embed)

client.loop.create_task(audio_player_task())

@client.command()
async def help():
    embed = discord.Embed(
        title = ':notes: Music For (your bot name here) :notes:',
        description = ':large_orange_diamond: Help Page For All Of The Commands! :large_orange_diamond: ',
        )
    embed.add_field(name='➜ -play', value='Plays the music', inline=False)
    embed.add_field(name='➜ -join', value='Joins the voice channel your in', inline=False)
    embed.add_field(name='➜ -leave', value='Leaves the voice channel', inline=False)
    embed.add_field(name='➜ -queue', value='Queues a video', inline=False)
    embed.add_field(name='➜ -pause', value='Pauses the current video', inline=False)
    embed.add_field(name='➜ -plays', value='Shows how many plays the video has', inline=False) 
    embed.add_field(name='➜ -skip', value='Skips the video to the next one queued', inline=False)
    embed.add_field(name='➜ -(add a command here)', value='Add your custom description here!', inline=False)
    await client.say(embed=embed)

@client.command(name="ban", pass_context=True)
async def _ban(ctx, user: discord.Member = None, *, arg = None):
    if ctx.message.author.server_permissions.ban_members == True:
        if user is None:
            await client.say("You have not chosen anyone to ban")
            return False
        if arg is None:
            await client.say("Reason to ban {}".format(user.name))
            return False
        reason = arg
        author = ctx.message.author
        await client.ban(user)
        embed = discord.Embed(title="Ban successful", description=" ", color=0xffffff)
        embed.add_field(name="User Banned: ", value="<@{}>".format(user.id), inline=False)
        embed.add_field(name="Banned By: ", value="{}".format(author.mention), inline=False)
        embed.add_field(name="Reason: ", value="{}\n".format(arg), inline=False)
        await client.say(embed=embed)

@client.command(name="kick", pass_context=True)
async def _kick(ctx, user: discord.Member = None, *, arg = None):
    if ctx.message.author.server_permissions.kick_members == False:
        if user is None:
            await client.say("You have chosen no one to kick")	
            return False
        if arg is None:
            await client.say("Reason to kick {}".format(user.name))
            return False
        reason = arg
        author = ctx.message.author
        await client.kick(user)
        embed = discord.Embed(title="Kick successful", description=" ", color=0x00ff00)
        embed.add_field(name="User Kicked: ", value="<@{}>".format(user.id), inline=False)
        embed.add_field(name="Kicked By: ", value="{}".format(author.mention), inline=False)
        embed.add_field(name="Reason: ", value="{}\n".format(arg), inline=False)
        await client.say(embed=embed)
    else:
        await client.send_message(ctx.message.channel, "Sorry {}, You don't have requirement permission to use this command `kick members`.".format(ctx.message.author.mention))

@client.command(pass_context = True)
async def bans(ctx):
    if ctx.message.author.server_permissions.ban_members == True:
        x = await client.get_bans(ctx.message.server)
        x = '\n'.join([y.name for y in x])
        embed = discord.Embed(title = "Ban list", description = x, color = 0x2c2f33)
        return await client.say(embed = embed)
        channel = client.get_channel('543488075809030145')
        embed = discord.Embed(title=f"User: {ctx.message.author.name} have used bans command", description=f"User ID: {ctx.message.author.id}", color=0xff9393)
        await client.send_message(channel, embed=embed)
    else:
        await client.send_message(ctx.message.channel, "Sorry {}, You don't have requirement permission to use this command `ban list`.".format(ctx.message.author.mention))

@client.command(name="clear", pass_context=True)
async def _clear(ctx, amount=50):
    if ctx.message.author.server_permissions.manage_messages == True:
        channel = ctx.message.channel
        messages = [ ]
        async for message in client.logs_from(channel, limit=int(amount) + 1):
            messages.append(message)
        await client.delete_messages(messages)
        msg = await client.say(f"{amount} have been purged!")
        await asyncio.sleep(5)
        await client.delete_message(msg)
        channel = client.get_channel('543488075809030145')
        embed = discord.Embed(title=f"User: {ctx.message.author.name} have used clean command", description=f"User ID: {ctx.message.author.id}", color=0xffffff)
        await client.send_message(channel, embed=embed)
    else:
    	await client.send_message(ctx.message.channel, "Sorry {}, You don't have requirement permission to use this command `manage messages`.".format(ctx.message.author.mention))

@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def setup(ctx):
    author = ctx.message.author
    server = ctx.message.server
    mod_perms = discord.Permissions(manage_messages=True, kick_members=True, manage_nicknames =True, mute_members=True)
    admin_perms = discord.Permissions(ADMINISTRATOR=True)
    
client.run('BOT_TOKEN') # <---- Paste your token here

