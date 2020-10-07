# bot.py
import os
import discord 
from discord.ext import commands
from discord.ext.commands import Greedy
from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool
import random
from contextlib import contextmanager
import datetime
import asyncio
from typing import Union


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


@bot.command(name = 'bunkers', aliases = ['bunker','bunkers'])
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
            channel = self.bot.get_channel(id=752711588586455110)
            await channel.send(f'{message.author.mention} is now level {user[-2]+1}')
        

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
            # channel = self.bot.get_channel(id=752711588586455110)
            sent = await ctx.channel.send(embed=embed)
            await sent.add_reaction(emoji = '\U0001f44d')


    @commands.command()
    async def leaderboard(self, ctx, members:Greedy[discord.Member]=None, how = 'me'):
        guild = ctx.guild
        guild_id = str(ctx.guild.id)
        place_msgs = []

        if how == 'me':
            members = ctx.author if not members else members

            if type(members) == discord.Member:
                members_id = [str(members.id)]
            else:
                members_id = [str(x.id) for x in members]

            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM level_system")
                all_users = cursor.fetchall()
                all_users = sorted(all_users, key= lambda x: x[-1], reverse = True)

                for member_id in members_id:
                    cursor.execute("SELECT * FROM level_system WHERE user_id = %s AND guild_id = %s", (member_id, guild_id))
                    user = cursor.fetchone()

                    if (not user) or (user is None):
                        await ctx.send('Member does not have a level in the database')
                        continue

                    idx = next(i for i, t in enumerate(all_users) if (t[0] == member_id) & (t[1] == guild_id))
                    idx += 1

                    if guild.get_member(int(member_id)).nick is not None:
                        name = guild.get_member(int(member_id)).nick
                    else:
                        name = guild.get_member(int(member_id)).name

                    msg = f'{name} is ranked {idx} on the leveling leaderboard at level {user[-2]} with {user[-1]} XP'
                    place_msgs.append(msg)

                final_message = '\n'.join(place_msgs)
                await ctx.send(final_message)

        elif how == 'all':
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM level_system")
                all_users = cursor.fetchall()

            all_users = sorted(all_users, key= lambda x: x[-1], reverse = True)

            for idx, user in enumerate(all_users, start = 0):
                
                if guild.get_member(int(user[0])).nick is not None:
                    name = guild.get_member(int(user[0])).nick
                else:
                    name = guild.get_member(int(user[0])).name

                idx += 1
                msg = f'{name} is ranked {idx} on the leveling leaderboard at level {user[-2]} with {user[-1]} xp'
                place_msgs.append(msg)

            final_message = '\n'.join(place_msgs)
            await ctx.send(final_message)


class matches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.team1 = None
        self.team2 = None
        self.team1_aliases = []
        self.team2_aliases = []

    @commands.command()
    async def set_teams(self, ctx, display_teams = None):
        guild = ctx.guild

        if display_teams is not None:
            if (self.team1 is None) or (self.team2 is None):
                await ctx.send('Teams have not been set. Please type !set_teams and follow prompts to set voice channel teams to log data from')
                return
            else:
                await ctx.send(f'Channels chosen for teams are set as:\n-Team 1: {guild.get_channel(self.team1).name}\n-Team 2: {guild.get_channel(self.team2).name}')
                return

        voice_channels = [x.name for x in guild.voice_channels]

        vc_dict = {}
        for i, vc in enumerate(voice_channels):
            vc_dict[str(i)] = vc
        
        vc_msg = [f'{k} : {v}' for k,v in vc_dict.items()]
        await ctx.send('Please enter the numbers for the channels that you want to set as the team channels with a comma serperating them e.g. 1,7 from the list below:\n\n' +'\n'.join(vc_msg) + '\n\nType "Cancel" to cancel')

        try:
            def check(m):
                return m.author == ctx.author

            msg = await self.bot.wait_for('message', check = check, timeout = 60.0)
        except asyncio.TimeoutError:
            await ctx.send('Team set timed out. You have 60 seconds to respond. Please type !set_teams if you would like to try again')
            return
        else:
            if msg.content.lower() == 'cancel':
                await ctx.send('Team setup canceled')
                return

            split_msg = msg.content.split(',')

            if len(split_msg) != 2:
                ctx.send('Please enter 2 channel numbers, seperated by a comma. e.g. 1,7')
                return
            
            team1, team2 = split_msg
            team1_id = discord.utils.get(guild.voice_channels, name = vc_dict[team1])
            team2_id = discord.utils.get(guild.voice_channels, name = vc_dict[team2])
            team1_id, team2_id = team1_id.id, team2_id.id
            self.team1, self.team2 = team1_id, team2_id
            await ctx.send(f'Channels chosen for teams are:\n-Team 1: {guild.get_channel(self.team1).name}\n-Team 2: {guild.get_channel(self.team2).name}')


    #TODO: Make logic for updating and deleting from the alias lists
    @commands.command()
    async def team_alias(self, ctx, method:str=None):
        guild = ctx.guild
        allowed_methods = ['update', 'delete', 'new']
        emojis = ['1️⃣', '2️⃣']
        emoji_dict = {emojis[0]:self.team1, emojis[1]:self.team2}
        emoji_alias_dict = {emojis[0]:self.team1_aliases, emojis[1]:self.team2_aliases}

        def msg_check(m):
            return m.author == ctx.author

        def reaction_check(reaction, user):
            return user == ctx.author and reaction.emoji in emojis
        
        if method is None:
            await ctx.send(f'Please specifiy one of the following when using the command to set the team alias: {", ".join(allowed_methods)}. This will indicate whether to start fresh, update the current alias list, or delete an alias from a list.')
            return
        elif method.lower() not in allowed_methods:
            await ctx.send(f'The allowable methods are {", ".join(allowed_methods)}')
            return
        
        if self.team1 is None or self.team2 is None:
            await ctx.send(f'Please setup teams before setting team aliases by using the !set_teams command')
            return


        sent = await ctx.send(f'-Team 1: {guild.get_channel(self.team1).name}\n-Team 2: {guild.get_channel(self.team2).name}\nReact with the number emoji corresponding to the team you want to make changes to.')
        for emoji in emojis:
            await sent.add_reaction(emoji)

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 30.0)
        except asyncio.TimeoutError:
            await ctx.send('Please react with one of the preset reacts')
            return
        else:
            await ctx.send(f'Thank you for reacting {reaction.emoji}')
            
        if method.lower() == 'new':
            try:
                await ctx.send('Please type the aliases to be used. Seperate names with a comma. Alias can be only 1 word. e.g. blue,blueteam,brs')
                msg = await self.bot.wait_for('message', check = msg_check, timeout = 120.0)
            except asyncio.TimeoutError:
                await ctx.send('Team set timed out. You have 60 seconds to respond. Please type !team_alias new if you would like to try again')
                return
            aliases = msg.content.split(',')

            await ctx.send(f'Team alias(es) for {guild.get_channel(emoji_dict[reaction.emoji]).name} will be set as {", ".join(aliases)}')
            emoji_alias_dict[reaction.emoji].extend(aliases)
            print(emoji_alias_dict[reaction.emoji])
        elif method.lower() == 'update':
            pass
        elif method.lower() == 'delete':
            pass
        else:
            await ctx.send('No action done to team alias')
            return

            
    @commands.command()
    async def scrimwin(self, ctx, type:Union[str,discord.Member]=None, winscore:str=None, gametype:str=None):
        pass


    #TODO: Can pass members, follow channel prompt to pull memembers names, or just use the msg author
    @commands.command()
    async def wzwin(self, ctx, members:Greedy[discord.Member] = None, channel:str=None):
        pass


class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        embed = discord.Embed(color = 0x95efcc,
            description=f'Welcome to the Bolt Rifle Squad/iONEi Discord server!\nYou are member number: {len(list(member.guild.members))}\nMake sure to enjoy your stay and check out our Call of Duty World at War Server with the !server command!',
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=f'New Member: {member.name}', icon_url=member.avatar_url)
        embed.set_footer(text=f'{member.guild}', icon_url=member.guild.icon_url)
        embed.set_thumbnail(url=f'{member.avatar_url}')
        channel = self.bot.get_channel(id=745331089375101036)
        sent = await channel.send(embed=embed)
        await sent.add_reaction(emoji = '👋')
        await channel.send(f'{member.mention} check out {self.bot.get_channel(id=530206822804750360).mention} to introduce yourself and make yourself at home!')

        await member.create_dm()
        await member.dm_channel.send(f'Hi {member.name}, welcome to {member.guild}! Please enjoy your stay!')


class battleground(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self
        
    @commands.command(help = 'Kill selected members with a random death, can be one member or multiple')
    async def kill(self, ctx, member:discord.Member = 340221274431160330):
        member = member if member == 340221274431160330 else member.id
        deaths = [
            'got run over by a car',
            'had their cheeks clapped',
            'took a arrow to the knee',
            'was found on the side of the road, pants down with a sore ass',
            'tripped and fell down the stairs like an idiot',
            'forgot to throw the grenade. Dumbass',
            "angered the robots, so BRSBot ended them with it's laser beams and saw hands"
        ]

        guild = ctx.guild
        member = guild.get_member(member)

        death = f'Looks like {member.mention} {random.choice(deaths)}'
        await ctx.send(death)


    @commands.command(help = 'Slap a member(s)')
    async def slap(self, ctx, members:Greedy[discord.Member],*,reason = 'no good reason'):
        slapped = ", ".join(x.name for x in members)
        await ctx.send('{} just got slapped for {}'.format(slapped, reason))


    @commands.command()
    async def battle(self, ctx, members:Greedy[discord.Member]):
        if len(members) <= 1:
            await ctx.send('Listen, you are gonna need more brave contestants than that. Come back with at least 2 people to duke it out.')
        else:
            fighters = ", ".join(x.name for x in members)
            winner = random.choice(members)
            message = f"""Ladies and Gentlemen, we have {len(members)} brave contestants entering into the ring, and only one can win.
            \nLooks like they are are all armed with rocks, paper, and scissors.
            \nAnd it looks like our winner is....{winner.name}!!!
            \nCongratulations {winner.mention}"""
            await ctx.send(message)


    @kill.error
    @slap.error
    @battle.error
    async def member_not_found(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('I could not find that member..., please use the @ mention system to specify member')


class HelpCommand(commands.HelpCommand):

    async def send_command_help(self, command):
        await self.get_destination().send(command.help)


bot.add_cog(matches(bot))
bot.add_cog(battleground(bot))
bot.add_cog(welcome(bot))
bot.add_cog(Levels(bot))

bot.run(TOKEN)
