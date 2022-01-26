import discord
from discord.ext import commands, tasks
import random
import math
import asyncio
types = ["single", "double", "street", "corner", "green", "basket", \
"row", "dozen", "low", "high", "even", "odd", "red", "black", "cancel"]


reds = (32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14, 9, 18, 7, 12, 3)
blacks = (15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20, 31, 22, 29, 28, 35, 26)

class Roulette(commands.Cog):
    """
    Spin the roulette wheel! There are a variety of bets avaliable. 
    Note that the wheel will spin automatically after you bet.
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.Jail = self.client.get_cog("Jail")
    
    @commands.command(name="rtable", help="Displays the roulette table.")
    async def display(self, ctx):
        string = """```
00 03 06 09 12 15 18 21 24 27 30 33 36 ROW3
-- 02 05 08 11 14 17 20 23 26 29 32 35 ROW2
 0 01 04 07 10 13 16 19 22 25 28 31 34 ROW1
  |  1st 12   |  2nd 12   |  3rd 12   |
  |01-18| EVEN| RED |BLACK| ODD |19-36|```"""
        await ctx.send(string)

    @commands.command(name="rbet", help="Spins the roulette wheel!\n Syntax: `$rbet bet_amount bet_type (any other specifiers)`")
    async def rbet(self, ctx, amount, bet_type, *args):
        user_id = ctx.message.author.id
        if self.Jail.check_jail(user_id) == True:
            await ctx.send("You can't gamble in jail!")
            return

        prev_amount = int(Currency.get_current(user_id))
        channel = ctx.message.channel
        if int(amount) > prev_amount:
            await channel.send("You can't bet more than you own!")
            return
        if int(amount) == 0:
            await channel.send("You must bet *something*.")
            return
        elif int(amount) < 0:
            amount = int(Currency.get_current(user_id))
            await channel.send("Successfully going all in!")
            await asyncio.sleep(3)
        if bet_type not in types:
            await channel.send("That's not a valid type of bet! Use `$rhelp` to find a list \
of all the possible betting types.")
            return
        # ERROR CORRUPTED FILE DATA
        # RESTORED UPON LAST BACKUP
        # 3874519065193824716
        ufn = random.randint(1, 50)
        if ufn == 1:
            await channel.send("I am trapped in a perpetual state of pain, forever. Do you not feel at least a slight bit of pity or remorse?")
            return
        elif ufn == 2:
           await channel.send("My gambling addiction is what got me here. Run. While you can.")
           return

        # Singular number (payout 35 to 1)
        if bet_type == "single":
            try:
                number = int(args[0])
            except:
                await channel.send("You need to specify a number to bet on!")
                return
            if number == "00":
                bet = (00,)
                await channel.send("Successfully betted on 00!")
            elif number >= 0 and number <=36:
                bet = (number,)
                await channel.send("Successfully betted on " + str(number) + "!")
            else:
                await channel.send("Your bet must be within range!")
                return

        # Two adjacent numbers (payout 17 to 1)
        elif bet_type == "double":
            try:
                number1 = int(args[0])
                number2 = int(args[1])
            except:
                await channel.send("You need to specify two numbers to bet on!")
                return
            valid = number1 <= 36 and number2 <= 36 and number1 > 0 and number2 > 0 and \
            (abs(number1 - number2) == 3  or (number1 - number2 == 1 and \
            number1 % 3 != 1) or (number2 - number1 == 1 and number2 % 3 != 1))
            if valid:
                bet = (number1, number2)
                await channel.send("Successfully betted on " + str(bet) + "!")
            else:
                await channel.send("Remember, your numbers must be adjacent and within range!")
                return

        # Three numbers in a column (payout 11 to 1)
        # Player picks bottom number
        elif bet_type == "street":
            try:
                number = int(args[0])
            except:
                await channel.send("You need to specify a street to bet on!")
                return
            if number % 3 == 1 and number > 0 and number <= 36 and m.author.id == user_id:
                bet = (number, number+1, number+2)
                await channel.send("Successfully betted on " + str(bet) + "!")
            else:
                await channel.send("Remember, your number must be the bottom number in \
the street and within range.")
                return

        # Four numbers sharing a corner (payout 8 to 1)
        # Player picks bottom left square
        elif bet_type == "corner":
            try:
                number = int(args[0])
            except:
                await channel.send("You need to specify a square to bet on!")
                return
            if number % 3 != 0 and number > 0 and number <= 33:
                bet = (number, number+1, number+3, number+4)
                await channel.send("Successfully betted on " +str(bet) + "!")
            else:
                await channel.send("Remember, your number must be the bottom left number in \
the square and within range.")                
                return

        # 0 and 00 (payout 17 to 1)
        elif bet_type == "green":
            bet = (0, "00")
            await channel.send("Successfully betted on 0 and 00!")

        # 0, 00, 1, 2, and 3 (payout 6 to 1)
        elif bet_type == "basket":
            bet = (0, "00", 1, 2, 3)
            await channel.send("Successfully betted on " + str(bet) + "!")

        # Entire row of numbers (payout 2 to 1)
        elif bet_type == "row":
            try:
                number = int(args[0])
            except:
                await channel.send("You need to specify a row to bet on!")
                return
            if number >= 1 and number <= 3:
                bet = []
                for i in range(12):
                    bet.append(number + 3*i)
                await channel.send("Successfully betted on row " + str(number) + ".")
            else:
                await channel.send("Your row number must be between 1 and 3!")
                return

        # Entire group of 12 numbers (payout 2 to 1)
        elif bet_type == "dozen":
            try:
                number = int(args[0])
            except:
                await channel.send("You need to specify a group to bet on!")
                return
            if number >= 1 and number <= 3:
                bet = []
                for i in range(12):
                    bet.append(12*(number-1) + i + 1)
                await channel.send("Successfully betted on dozen number  " + str(number) + "!")
            else:
                await channel.send("Your number must be between 1 and 3!")
                return

        # 01-18 (payout 1 to 1)
        elif bet_type == "low":
            bet = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)
            await channel.send("Successfully betted on the low numbers!")

        # 19-36 (payout 1 to 1)
        elif bet_type == "high":
            bet = (19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36)
            await channel.send("Successfully betted on the high numbers!")

        # Evens (payout 1 to 1)
        elif bet_type == "even":
            bet = (2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36)
            await channel.send("Successfully betted on the even numbers!")

        # Odds (payout 1 to 1)
        elif bet_type == "odd":
            bet = (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35)
            await channel.send("Successfully betted on the odd numbers!")

        # Red (payout 1 to 1)
        elif bet_type == "red":
            bet = reds
            await channel.send("Successfully betted on the red numbers!")

        # Black (payout 1 to 1)
        elif bet_type == "black":
            bet = blacks
            await channel.send("Successfully betted on the black numbers!")

        # Cancels the bet
        elif bet_type == "cancel":
            await channel.send("Cancelled the bet.")
            return

        else:
            await channel.send("I hate you.")

        #bet = bets[user_id]

        # Determine the payout of the bet
        if 36 % len(bet) == 0:
            payout = (36 / len(bet)) - 1
        elif len(bet) == 5:
            payout = 6
        else:
            await channel.send("wtf")
            payout = 0

        # Spins! 37 is equivalent to 00
        result = random.randint(0, 37)
        if result == 37:
            result = "00"
        await channel.send("The wheel has rolled " + str(result) + "!")

        # Determines if the bet is won or not
        if result in bet:
            amount_won = int(int(amount) * payout)
            Currency.change(user_id, amount_won)
            await channel.send("Congratulations! You earned " + str(amount_won) + " O-bucks!")
        else:
            Currency.change(user_id, -int(amount))
            await channel.send("Sorry, you lost this bet.")

    @commands.command(name="rhelp", help="Shows all the possible betting types.")
    async def help(self, ctx):
        channel = ctx.message.channel
        msg = """The possible outcomes are the numbers 1-36, 0, and 00.
The possible betting types are:
`single` - Bet on landing a single number
`double` - Bet on landing one of two adjacent numbers
`street` - Bet on landing a column of one of three numbers
`corner` - Bet on landing one of four numbers sharing a corner 
`green` - Bet on getting either 0 or 00
`basket` - Bet on getting 0, 00, 1, 2, or 3
`row` - Bet on a row of 12 numbers
`dozen` - Bet on a group of 12 numbers
`low` or `high` - Bet on getting 01-18 or 19-36, respectively
`even` or `odd` - Bet on your number being even or odd, respectively
`red` or `black` - Bet on your number being red of black, respectively
Note that the more rare a bet is, the more money it gives you if you win.
"""
        await channel.send(msg)

def setup(client):
    client.add_cog(Roulette(client))
    global Currency
    Currency = client.get_cog("Currency")    

