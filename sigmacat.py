import discord
from discord.ext import commands
import random
import os
import keep_alive

instructions = "To play **Reaper** (\"reap\"):\n\
Reap by typing reap. The amount of points you can get from a single reap \
is the exact number of seconds since the previous person reaped. The winner \
is the first to a set amount of points. \n\
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
To end the game at any time, simply input -1 when asked for row/column number. \
"

client = commands.Bot(command_prefix = "$")

async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

async def unload(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command(name="ligma")
async def ligma(ctx: commands.Context):
    await ctx.send("balls")

@client.command(name="howto")
async def howto(ctx:commands.Context):
    await ctx.send(instructions)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")
        print(f"cogs.{filename[:-3]}")

keep_alive.keep_alive()

client.run('token')


