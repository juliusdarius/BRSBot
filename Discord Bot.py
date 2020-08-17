# bot.py
import os
import discord 
from discord.ext import commands
from dotenv import load_dotenv
import random
import re


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

bot = commands.Bot(command_prefix='!')

@client.event
async def on_ready():

    guild = discord.utils.get(client.guilds, name=GUILD)
    await client.change_presence(activity=discord.Game(name='Searching for Pip'))

    if guild:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')


# @client.event
# async def on_member_join(member):
#     await member.create_dm()
#     await member.dm_channel.send(f'Hi {member.name}, welcome to PALS 4 LIFE! Please enjoy your stay!')


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
    
#     guild = discord.utils.get(client.guilds, name=GUILD)
#     game_time =["Better toggle off","Sounds like someone needs to get better at the game...","Don't hate the player, hate the game","Gotta play with the best to become the best"]

#     print(message.content, type(message.content))
#     members = [[member.nick,member.name] for member in guild.members]
#     print(members)

#     if ('hack' in message.content.lower()):
#         response = random.choice(game_time)
#         await message.channel.send(response)


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     guild= discord.utils.get(client.guilds, name = GUILD)

#     if 'user nicknames' in message.content.lower():
#         members = [[member.name, member.nick] for member in guild.members]
#         for member,nick in members:
#             if nick is not None:
#                 await message.channel.send(f'{member} goes by the nickname {nick}')
#             else:
#                 await message.channel.send(f'{member} does not have a nickname')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    guild = discord.utils.get(client.guilds, name = GUILD)

    if 'user activities' in message.content.lower():
        members = [[member, member.activities] for member in guild.members]
        for member,activity in members:
            if activity:
                # await message.channel.send(f'{member.nick} is doing: {activity}')
                print(f'{member.nick} is doing: {activity}')
                print(type(activity))


@bot.command(name = 'teamgen')
async def team_gen(ctx, *teams):
#TODO: Get the current list of members in the CoD voice server and then move only the members of that channel
#TODO: Pull from Scrim team 1 and 2 to get the teamlist for reshuffle
    teams = list(teams)
    guild = discord.utils.get(bot.guilds, name = GUILD)

    channels = []
    channel_ids = []
    for channel in guild.channels:
        if (channel.type == discord.ChannelType.voice) and ('scrim' in channel.name.lower()):
            channels.append(channel.name)
            channel_ids.append(channel.id)

    cod_channel = discord.utils.get(guild.channels, name = 'CALL OF DUTY')
    print([x.id for x in cod_channel.members])
    teams = [str(x.id) for x in cod_channel.members]

    if len(teams) % 2 == 0:
        random.shuffle(teams)
        team1 = teams[:(len(teams) // 2)]
        team2 = teams[len(teams) //2:]
        # print(team1, team2)
    else:
        random.shuffle(teams)
        x = len(teams) // 2
        y = (len(teams) // 2) + 1
        lens = [x,y]
        random.shuffle(lens)
        team1 = teams[:lens[0]]
        team2 = teams[lens[0]:]
        # print(team1,team2)

    print(team1,team2)
    t1 = '\n'.join([f'- <@!{x}>' for x in team1])
    t2 = '\n'.join([f'- <@!{x}>' for x in team2])

    await ctx.send(f"Team 1 in {channels[0]}:\n{t1}\n\nTeam 2 in {channels[-1]}:\n{t2}")

    t1_ids = [int(''.join(x for x in i if x.isdigit())) for i in team1]
    t2_ids = [int(''.join(x for x in i if x.isdigit())) for i in team2]

    teams = [t1_ids,t2_ids]

    for team, channel_id in zip(teams,channel_ids):
        channel = bot.get_channel(channel_id)
        for id_ in team:
            member = guild.get_member(id_)
            if member is not None:
                await member.move_to(channel)

@bot.command(name = 'test')
async def test(ctx):
    await ctx.send('Yea yea, I hear you')


bot.run(TOKEN)
