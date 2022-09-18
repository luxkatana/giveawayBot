import discord
import random
from discord.ext import commands
import asyncio
from time import time
import datetime as dt
from datetime import datetime
from  views import *

from dotenv import load_dotenv

import os

load_dotenv()
TOKEN = os.environ["TOKEN"]
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="./", intents=intents,
                   activity=discord.Game(name="giving stuff away :tadaa:"))

async def convert(victim: list[str]) -> int:
  pos = ["s","m","h","d"]
  '''
  s = seconds
  m = months
  h = hours
  d = days
  
  Inspired my .InvalidPeyton ツ#6003
  '''
  time_dict = {"s" : 1, "m" : 60, "h" : 3600, "d": 3600*24}
  unit: str = ""
  val: int = 0
  for  this in victim:
    unit = this[-1]
    if unit not in this:
        return -1
    try:
        val += int(this[:-1])
    except:
        return -2

  return val * time_dict[unit]

async def getHHMMSSFormat(totalseconds: int) -> str:
    '''
    :param totalseconds:
    PS: Legit copied this function somewhere because im bad in datetimes and times
    '''
    duration = dt.timedelta(seconds=totalseconds)
    timePeriod = (datetime.min + duration).time()
    return timePeriod.isoformat(timespec="seconds")
SERVERS = [941803156633956362]
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} on file {__file__}")

@bot.slash_command(name="start_giveaway", guild_ids=SERVERS)
@discord.option(name="name", description="name of the giveaway", type=str, max_length=256, required=True)
@discord.option(name="winners", description="amount of winners(max 5)", type=str, required=True, max_length=1)
@discord.option(name="what_to_win", description="prize of the giveaway", required=True, max_length=100)
@discord.option(name="duration", description="duration of the giveaway (h|d|m|s) seperate with ',' for next time")
@discord.option(name="duration_in_time", description="the duration option but the number", required=True)
@discord.option(name="channel", description="the channel where the giveaway will start", required=True, type=discord.TextChannel)
async def start_giveaway(ctx: discord.ApplicationContext, name: str, winners: str, duration: str, what_to_win: str, channel: discord.TextChannel) -> None:
    ALLOWED_ROLES = [945370507476344863]
    for role in ctx.author.roles:
        if role.id in ALLOWED_ROLES:
            break
    else:
        ssh = discord.Embed(title="Failed", description="You dont have any allowed role(s) for this command", colour=discord.Color.red())
        await ctx.respond(embed=ssh)
        return

    if winners.isnumeric():
        casted = int(winners)
        if casted  < 5:
            embed = discord.Embed(title=name, colour=discord.Color.green())
            splitted = duration.split(",")
            duration_seconds = await convert(splitted)
            match duration_seconds:
                case -1:
                    await ctx.respond('''
invalid unit\nYou can use these units:\n
s - seconds
m - minutes
h - hours
d - days
''', ephemeral=True)
                    return
                case -2:
                    await ctx.respond("duration must be a number/integer not character", ephemeral=True)
                    return
                case _:
                    formatted_time = await getHHMMSSFormat(duration_seconds)
                    embed = discord.Embed(title=name, colour=discord.Color.green())
                    ends_at_t = time() + int(duration_seconds)
                    hours, minutes, seconds = formatted_time.split(":")
                    embed.add_field(name="duration", value=f"{hours} hours {minutes} minutes and {seconds} seconds",inline=False)
                    embed.add_field(name="hosted by ", value=f"<@{ctx.author.id}>", inline=True)
                    embed.add_field(name="amount of winners", value=f"*{winners}*")
                    embed.add_field(name="participants joined", value="0")
                    try:
                        v = giveaway_view(duration_seconds, embed)
                        message = await channel.send(embed=embed, view=v)
                        
                    except:
                        await ctx.respond("Couldnt send in {}".format(channel), ephemeral=True)
                        return
                    await ctx.respond(f"created: {message.jump_url}", ephemeral=True)
                    editable = duration_seconds

                    while editable > 0:
                        editable -= 1
                        if editable % 10 == 0:
                            conv = await getHHMMSSFormat(editable)
                            hours, minutes, seconds = conv.split(":")
                            new_generated_shit = discord.Embed(title=name, colour=discord.Color.green())
                            new_generated_shit.add_field(name="duration", value=f"{hours} hour(s) {minutes} minute(s) and {seconds} second(s)", inline=False)
                            new_generated_shit.add_field(name="hosted by ", value=f"<@{ctx.author.id}>", inline=True)
                            new_generated_shit.add_field(name="amount of winners", value=f"*{winners}*")
                            new_generated_shit.add_field(name="participants joined",
                                                         value=len(v.joined))
                            await message.edit(embed=new_generated_shit)
                        await asyncio.sleep(1)
                    all_joined = v.joined
                    if len(all_joined) <= int(winners):
                        await message.edit(embed=discord.Embed(title="Giveaway Failed", description="Not enough people to win", colour=discord.Color.red()), view=None)
                    else:
                        
                        rand_winners = random.choice(all_joined)
                        all_w = []
                        for i in range(0, int(winners)):
                            random_number = random.choice(all_joined)
                            while random_number in all_w:
                                random_number = random.choice(al)
                            all_w.append(f"<@{random_number}>")

                        emb = discord.Embed(title=":tadaa: Giveaway Ended :tadaa:", description=f"winners:\n".join(all_w), colour=discord.Color.green(), timestamp=datetime.now())
                        emb.add_field(name="Prize", value=f"*{what_to_win}*", inline=True)
                        emb.add_field(name="Hosted by", value=f"<@{ctx.author.id}>", inline=True)
                        await message.edit(embed=emb, view=None)
                        return
        else:
            await ctx.respond("5 winners are allowed not **{}**".format(winners), ephemeral=True)
    else:
        await ctx.respond("``winners`` must be a number", ephemeral=True)
bot.run(TOKEN)