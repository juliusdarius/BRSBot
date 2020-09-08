# bot.py
import os
import discord 
from discord.ext import commands
from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool
import random
from contextlib import contextmanager
import datetime


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
USER = os.getenv('POSTGRESQL_USER')
PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
POSTGRESQL_HOST = os.getenv('POSTGRESQL_HOST')
POSTGRESQL_PORT = os.getenv('POSTGRESQL_PORT')


client = discord.Client()

bot = commands.Bot(command_prefix='!')

last_team = None

team_names = ['Allegiance','Coalition']


@bot.command(name = 'server')
async def brs_server(ctx):
    server_ip = '173.199.88.50:28960'
    server_name = 'iONEi | BOLTS ONLY | EASTCOAST #1'
    await ctx.send(f'Join us in Call of Duty World at War!\nServer IP: {server_ip}\nServer Name: {server_name}')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Searching for Pip'))


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to PALS 4 LIFE! Please enjoy your stay!')


@bot.command(name = 'teamgen')
async def team_gen(ctx, *args, last_team = last_team,):
#TODO: Get the current list of members in the CoD voice server and then move only the members of that channel
#TODO: Pull from Scrim team 1 and 2 to get the teamlist for reshuffle
    # print(args)
    guild = discord.utils.get(bot.guilds, name = GUILD)

    team_player_dict = {}
    cod_channel = None
    channels = []
    channel_ids = []

    for channel in guild.channels:
        print(channel.name, "call of duty" in channel.name.lower())
        if "call of duty" in channel.name.lower():
            cod_channel = channel
        if (channel.type == discord.ChannelType.voice) and ('scrim' in channel.name.lower()):
            channels.append(channel.name)
            channel_ids.append(channel.id)

    teams = [str(x.id) for x in cod_channel.members]

    if (args[0] == 'new') or (not args):
        if len(teams) % 2 == 0:
            random.shuffle(teams)
            team1 = teams[:(len(teams) // 2)]
            team2 = teams[len(teams) //2:]
        else:
            random.shuffle(teams)
            x = len(teams) // 2
            y = (len(teams) // 2) + 1
            lens = [x,y]
            random.shuffle(lens)
            team1 = teams[:lens[0]]
            team2 = teams[lens[0]:]

        t1 = '\n'.join([f'- <@!{x}>' for x in team1])
        t2 = '\n'.join([f'- <@!{x}>' for x in team2])

        await ctx.send(f"Team 1 ({team_names[0]}) in {channels[0]}:\n{t1}\n\nTeam 2 ({team_names[1]}) in {channels[-1]}:\n{t2}")

        t1_ids = [int(''.join(x for x in i if x.isdigit())) for i in team1]
        t2_ids = [int(''.join(x for x in i if x.isdigit())) for i in team2]

        teams = [t1_ids,t2_ids]

        for team, channel_id in zip(teams,channel_ids):
            channel = bot.get_channel(channel_id)
            team_player_dict[channel_id] = [x.id for x in team]
            for id_ in team:
                member = guild.get_member(id_)
                if member is not None:
                    await member.move_to(channel)
                    

    elif (args) and (args[0] == 'old') and (last_team is not None):
        team_player_dict = last_team
        for team in team_player_dict.values():
            for id_ in team:
                member = guild.get_member(id_)
                if member is not None:
                    await member.move_to(bot.get_channel(cod_channel))
    else:
        return


@bot.command(name = 'shuffle_teams')
async def reshuffle_teams(ctx):
#TODO: Pull from Scrim team 1 and 2 to get the teamlist for reshuffle
    guild = discord.utils.get(bot.guilds, name = GUILD)
    channels = []
    channel_ids = []
    teams = []
    for channel in guild.channels:
        if (channel.type == discord.ChannelType.voice) and ('scrim' in channel.name.lower()):
            channels.append(channel.name)
            channel_ids.append(channel.id)
            teams.extend([str(x.id) for x in channel.members])

    if len(teams) == 0:
        return

    if len(teams) % 2 == 0:
        random.shuffle(teams)
        team1 = teams[:(len(teams) // 2)]
        team2 = teams[len(teams) //2:]
    else:
        random.shuffle(teams)
        x = len(teams) // 2
        y = (len(teams) // 2) + 1
        lens = [x,y]
        random.shuffle(lens)
        team1 = teams[:lens[0]]
        team2 = teams[lens[0]:]

    t1 = '\n'.join([f'- <@!{x}>' for x in team1])
    t2 = '\n'.join([f'- <@!{x}>' for x in team2])

    await ctx.send(f"Team 1 ({team_names[0]}) in {channels[0]}:\n{t1}\n\nTeam 2 ({team_names[1]}) in {channels[-1]}:\n{t2}")

    t1_ids = [int(''.join(x for x in i if x.isdigit())) for i in team1]
    t2_ids = [int(''.join(x for x in i if x.isdigit())) for i in team2]

    teams = [t1_ids,t2_ids]

    for team, channel_id in zip(teams,channel_ids):
        channel = bot.get_channel(channel_id)
        for id_ in team:
            member = guild.get_member(id_)
            if member is not None:
                await member.move_to(channel)


@bot.command(name = 'debrief')
async def rejoin_scrim_teams(ctx, *args):
#TODO: Pull from Scrim team 1 and 2 to get the teamlist for reshuffle
    guild = discord.utils.get(bot.guilds, name = GUILD)

    team_player_dict = {}
    for channel in guild.channels:
        if (channel.type == discord.ChannelType.voice) and ('scrim' in channel.name.lower()):
            team_player_dict[channel.id] = [x.id for x in channel.members]


    for channel in guild.channels:
        if "call of duty" in channel.name.lower():
            cod_channel = channel.id

    # print(team_player_dict, cod_channel)

    if not team_player_dict:
        return

    if cod_channel is None:
        await ctx.send('No call of duty channel. Ensure there is a Call of Duty channel')
        return

    last_team = team_player_dict

    for team in team_player_dict.values():
        for id_ in team:
            member = guild.get_member(id_)
            if member is not None:
                await member.move_to(bot.get_channel(cod_channel))


@bot.command(name = 'test')
async def test(ctx):
    await ctx.send('Yea yea, I hear you')


@bot.command(name = 'bunkers')
async def send_bunker_map(ctx, *bunker_num):

    codes_dict = {
        'B7':'97264138',
        'H6':'49285163',
        'B5':'87624851',
        'H8':'72948531',
        'F4':'27495810',
        'F8':'60274513'
    }

    if bunker_num:
        bunker_num = bunker_num[0]
        if bunker_num.upper() in codes_dict:
            await ctx.send(f'The bunker code for grid mark {bunker_num.upper()} is {codes_dict.get(bunker_num.upper())}')
        else:
            valid_codes = "\n".join(["- " + code for code in codes_dict.keys()])
            await ctx.send(f'The acceptable grid mark locations are\n{valid_codes}')
    else:
        await ctx.send(file = discord.File('Bunkers.png'))


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        USER = os.getenv('POSTGRESQL_USER')
        PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
        POSTGRESQL_HOST = os.getenv('POSTGRESQL_HOST')
        POSTGRESQL_PORT = os.getenv('POSTGRESQL_PORT')
        self.db_connection = pool.SimpleConnectionPool(1,10,user = USER, password = PASSWORD, host = POSTGRESQL_HOST, port = POSTGRESQL_PORT, database = 'BRSBotDB')


    @contextmanager
    def get_cursor(self):
        conn = self.db_connection.getconn()
        try:
            yield conn.cursor()
            conn.commit()
        finally:
            self.db_connection.putconn(conn)


    def level_up(self, user):
        curr_xp = user[-1]
        curr_level = user[-2]

        if curr_xp >= round((4*(curr_level**3)) / 5):
            with self.get_cursor() as cursor:
                cursor.execute("UPDATE level_system SET level = %s WHERE user_id = %s AND guild_id = %s", (user[-2]+1, user[0], user[1]))
            return True
        else:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == bot.user:
            return

        author_id = str(message.author.id)
        guild_id = str(message.guild.id)

        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM level_system WHERE user_id = %s AND guild_id = %s", (author_id, guild_id))
            user = cursor.fetchall()

            if (not user) or (user is None):
                cursor.execute("INSERT INTO level_system (user_id,guild_id,level,xp) VALUES (%s,%s,1,0)", (author_id,guild_id))

            cursor.execute("SELECT * FROM level_system WHERE user_id = %s AND guild_id = %s", (author_id, guild_id))
            user = cursor.fetchone()
            new_xp = user[-1]+1
            cursor.execute("UPDATE level_system SET xp = %s WHERE user_id = %s AND guild_id = %s", (new_xp, author_id, guild_id))

        if self.level_up(user):
            await message.channel.send(f'{message.author.mention} is now level {user[-2]+1}')
        

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        member_id = str(member.id)
        guild_id = str(ctx.guild.id)

        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM level_system WHERE user_id = %s AND guild_id = %s", (member_id, guild_id))
            user = cursor.fetchone()

        if not user:
            await ctx.send('Member does not have a level')
        else:
            embed = discord.Embed(color = member.color, timestamp=ctx.message.created_at)
            embed.set_author(name=f'User - {member}', icon_url=self.bot.user.avatar_url)
            embed.add_field(name='Level', value=user[-2])
            embed.add_field(name='XP', value=user[-1])
            channel = self.bot.get_channel(id=752711588586455110)
            sent = await channel.send(embed=embed)
            await self.bot.add_reaction(sent, emoji = "\U0001F44D")



class match(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

            embed = discord.Embed(color = 0x95efcc,
                description=f'Welcome to the Bolt Rifle Squad/iONEi Discord server!\nYou are member number: {len(list(member.guild.members))}\nMake sure to enjoy your stay and check out our Call of Duty World at War Server with the !server command!',
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=f'New Member {member.name}', icon_url=member.avatar_url)
            embed.set_footer(text=f'{member.guild}', icon_url=member.guild.icon_url)
            embed.set_thumbnail(url=f'{member.avatar_url}')
            channel = self.bot.get_channel(id=530206822804750360)
            sent = await channel.send(embed=embed)
            await self.bot.add_reaction(sent, emoji = "\U0001F44D")


bot.add_cog(welcome(bot))
bot.add_cog(Levels(bot))

bot.run(TOKEN)
