import discord
from discord.ext import commands, tasks
import random
bets = {}
amounts = {}
types = ["single", "double", "street", "corner", "line", \
"row", "dozen", "low", "high", "even", "odd", "red", "black"]

class Roulette(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="rtable")
    async def display(self, ctx):
        string = """```
00 03 06 09 12 15 18 21 24 27 30 33 36 ROW3
-- 02 05 08 11 14 17 20 23 26 29 32 35 ROW2
 0 01 04 07 10 13 16 19 22 25 28 31 34 ROW1
  |  1st 12   |  2nd 12   |  3rd 12   |
  |01-18| EVEN| RED |BLACK| ODD |19-36|```"""
        await ctx.send(string)

    @commands.command(name="rbet")
    async def bet(self, ctx, amount):
        user_id = ctx.message.author.id
        channel = ctx.message.channel
        def check(m):
            print(m.content)
            if m.content in types:
                return True
            else:
                return False
        await channel.send("Pick a type of bet.")
        msg = await self.client.wait_for("message", check=check)
        if msg.content == "single":
            def check_single(m):
                if m.content == "00":
                    return True
                try:
                    number = int(m.content)
                except:
                    return False
                if number >= 0 and number <= 36:
                    return True
                else:
                    return False
            await channel.send("Pick a singular number to bet on.")
            number = await self.client.wait_for("message", check=check_single)
            number = number.content
            print(number)
            if number == "00":
                Roulette.add_bet(self, user_id, "00",)
                await channel.send("Successfully betted on 00!")
            elif int(number) >= 0 and int(number) <=36:
                Roulette.add_bet(self, user_id, (int(number),))
                await channel.send("Successfully betted on " + number + "!")
            else:
                await channel.send("For whatever reason, your bet was not successful.")
        elif msg.content == "double":
            def check_double(m):
                try:
                    number1 = int(m[0:2])
                    number2 = int(m[3:5])
                except:
                    return False
                if number1 <= 36 and number2 <= 36 and number1 > 0 and number2 > 0 and \
                (abs(number1 - number2) == 3  or (number1 - number2 == 1 and \
                (number1 % 3 == 0 or number1 % 3 == 2)) or (number2 - number1 == 1 and \
                (number2 % 3 == 0 or number2 % 3 == 2))):
                    return True
                else: 
                    return False
            numbers = await self.client.wait_for("message", check=check_double)
            number1 = int(numbers[0:2])
            number2 = int(numbers[3:5])
            bet[user_id] = (number1, number2)

    # Adds the bet to the dictionary, creates a new key if
    # does not already exist. Note: "bet" is a tuple.
    def add_bet(self, user_id, bet):
        if user_id not in bets:
            bets[user_id] = []
        bets[user_id].append(bet)
        print(bets)



def setup(client):
    client.add_cog(Roulette(client))    