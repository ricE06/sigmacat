import discord
from discord.ext import commands
import random
import os
import keep_alive
import asyncio
import time

instructions = "To play **Reaper** (\"reap\"):\n\
Reap by typing `reap`. The amount of points you can get from a single reap \
is the exact number of seconds since the previous person reaped. The winner \
is the first to a set amount of points. \
Other commands can be found in the channel description.\n\
Some reaper games can be *monetized*, meaning that you must pay a certain number \
of O-bucks to reap in them. The O-bucks remain in a prize pool until the game \
*is played to completion*, when they will be distributed among the players \
based on their scores and a couple other additional factors (such as ranking).\n\
To play **Greed Control** ($greed):\n\
Each day, pick a number. The points you earn at the end of the day is equal to the number you picked, divided by the number of players that also picked your number.\n\
To play **Five-by-Five** ($five):\n\
25 cards will be drawn from 40 cards (face cards removed). Aces are \
worth one and all others are worth their numerical values. After each card is \
drawn, the player must choose an empty location on their five by five grid to \
place the card. Once all 25 cards have been placed, points will be calculated \
for each row and each column as the sum of all *sets of 2 or more adjacent* equal numbers. \
For example, [4, 4, 5, 7, 1] gives 8 points and [7, 9, 9, 9, 2] gives 27 points. \
Rows or columns without any adjacent lines give no points. \
The goal is to get the largest point value. \
The labeling for the grid is **0-4** rows, **0-4** columns. \n\
To place a card, use `$fplace [row number] [column number]`. \n\
To end the game at any time, simply type `$fend`. \
"
token = open("token.txt", "r").read()
intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

async def unload(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

@bot.command(name="ligma")
async def ligma(ctx: commands.Context):
    await ctx.send("balls")

@bot.command(name="howto")
async def howto(ctx:commands.Context):
    await ctx.send(instructions)

@bot.command(name="reload")
async def reload(ctx:commands.Context):
    if filename.endswith(".py"):
        bot.unload_extension(f"cogs.{filename[:-3]}")
        bot.load_extension(f"cogs.{filename[:-3]}")
        print(f"cogs.{filename[:-3]}")    

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

required_in_order = ("Jail", "Currency")

for cog in required_in_order:
    bot.load_extension("cogs." + cog)
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and filename[:-3] not in required_in_order:
        bot.load_extension(f"cogs.{filename[:-3]}")
        print(f"cogs.{filename[:-3]}")

@bot.command()
async def help(ctx, inp = None):
    if not inp:
        emb = discord.Embed(title="Help", color=discord.Color.blue(), description="A bot for [some of] your needs!")

        cogs_desc = ''
        for cog in bot.cogs:
            cogs_desc += f'**{cog}**: {bot.cogs[cog].description}\n'

        emb.add_field(name="Modules", value=cogs_desc, inline=False)

        commands_desc = ''
        for command in bot.walk_commands():
            if not command.cog_name and not command.hidden:
                commands_desc += f'**{command.name}**: {command.help}\n'

        if commands_desc:
            emb.add_field(name="Misc. commands", value=commands_desc, inline=False)
    else:
        for cog in bot.cogs:
            if cog.lower() == inp.lower():
                emb = discord.Embed(title=f'{cog}', description=bot.cogs[cog].__doc__, color=discord.Color.green())

                for command in bot.get_cog(cog).get_commands():
                    if not command.hidden:
                        emb.add_field(name=command.name, value=command.help, inline=False)

                break

            else:
                emb = discord.Embed(title="Error!", description=f'Could not find {inp}', color=discord.Color.red())

    await ctx.send(embed=emb)


# keep_alive.keep_alive()

# things that need to run every 24 hours
Currency = bot.get_cog("Currency")
Greed = bot.get_cog("Greed")
async def lol():
    current = time.ctime()
    s = int(current[17:19])
    m = int(current[14:16])
    h = int(current[11:13])
    wait = (23-h)*3600+(59-m)*60+s
    print(wait)
    if wait < 1:
       wait = 24*60*60
    print(wait)
    await asyncio.sleep(wait)
    await Currency.bank_update()
    await Greed.give_points()
    await asyncio.sleep(30)

bot.loop.create_task(lol())
bot.run(token)
print("yay")





