import sqlite3
import discord
from discord.ext import commands, tasks
from datetime import date
import math
con = sqlite3.connect('currencies.db')
cur = con.cursor()

DAILY_AMOUNT = 1000


# noinspection PyUnresolvedReferences
class Currency(commands.Cog, description="o-bucks"):
    """
    o-bucks
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="balance", help="Displays the current balance of a user\nSyntax: `$balance` or `$balance @user`")
    async def show_balance(self, ctx, usr: discord.Member=None):
        if usr is None:
            usr = ctx.author

        await ctx.send(usr.name + " currently has " + str(Currency.get_current(self, usr.id)) + " O-bucks.")

    @commands.command(name="daily", help="Adds 1000 to a user if they have not used this command within the last 24\nSyntax: `$daily`")
    async def give_daily(self, ctx:commands.Context):
        user_id = ctx.message.author.id
        last_daily = Currency.get_last_daily(self, user_id)
        current_date = str(date.today())
        if last_daily == current_date:
            await ctx.send("You've already collected your daily today you greedy piece of shit!")
        else:
            new = Currency.get_current(self, user_id) + DAILY_AMOUNT
            Currency.update(self, user_id, new)
            cur.execute("UPDATE balances SET lastDaily=? WHERE user=?", (str(current_date), user_id))
            con.commit()
            await ctx.send("Successfully deposited 1000 O-bucks!")

    # untested function
    @commands.command(name="give", help="Give some amount of money to another person\nSyntax: `$give @user amount`")
    async def give_money(self, ctx, user: discord.Member, bal):
        # limit tbd 
        # how it would work:
        # if self.check_limit(receiver, bal):
        #     await ctx.send("You sure have a lot of fans, huh.")
        #     return
        # but below the statements below lol

        # check_limit command:
        # untested & more logic + safety can be used, but it's the general idea
        # def check_limit(self, id, bal):
        #     cur.execute("SELECT * FROM balances WHERE user=?", (user_id,))
        #     a = cur.fetchone()[3]
        #     if a + bal > limit:
        #         return True 
        #     return False

        giver = ctx.author.id 
        receiver = user.id 

        try:
            bal = int(bal)
        except:
            await ctx.send("bro money is measured in dollars, not whatever the fuck you just gave me")
            return

        if bal < 0:
            await ctx.send("You're an asshole.")
            return

        if self.get_current(giver) < bal:
            await ctx.send("If money grew on trees, you need more trees.")
            return 


        give_amount = math.floor(bal*0.90)
        self.change(giver, -bal)
        self.change(receiver, give_amount)

        await ctx.send(ctx.author.name + " successfully gave " + str(user.name) + " " + str(give_amount) + " o-bucks!")




    # Makes a table
    def create(self):
        cur.execute("""CREATE TABLE balances (
                    user integer,
                    amount integer
                    )""")
        con.commit()

    # Gets the current account balance of a user
    def get_current(self, user_id):
        users = Currency.get_users(self)
        if user_id in users:
            cur.execute("SELECT * FROM balances WHERE user=?", (user_id,))
            return cur.fetchone()[1]
        else:
            return 0

    # Gets the last time a user used the daily function (returns string)
    def get_last_daily(self, user_id):
        users = Currency.get_users(self)
        if user_id in users:
            cur.execute("Select * FROM balances WHERE user=?", (user_id,))
            return str(cur.fetchone()[2])
        else:
            return "0"

    # Inserts new row
    def add_row(self, user_id, balance):
        sql = "INSERT INTO balances VALUES(?, ?, ?)"
        cur.execute(sql, (user_id, balance, 0))
        con.commit()

    # Updates balance of a user
    def update_balance(self, user_id, new):
        sql = "UPDATE balances SET amount=? WHERE user = ?"
        cur.execute(sql, (new, user_id))
        con.commit()

    # Adds a row or updates an existing one for a user (use this one)
    def update(self, user_id, balance):
        users = Currency.get_users(self)
        if user_id in users:
            Currency.update_balance(self, user_id, balance)
        else:
            Currency.add_row(self, user_id, balance)

    # Changes the user's balance by an amount (can be negative)
    def change(self, user_id, change):
        balance = Currency.get_current(self, user_id)
        new_balance = round(balance + change)
        # Cannot dip below zero
        if new_balance < 0:
            new_balance = 0
        Currency.update(self, user_id, new_balance)

    # Returns a list of all users in the table
    def get_users(self):
        rows = Currency.get_full(self)
        users = []
        for row in rows:
            users.append(row[0])
        return users

    # Returns the entire table    
    def get_full(self):
        cur.execute("SELECT * FROM balances")
        rows = cur.fetchall()
        return rows

def setup(client):
    client.add_cog(Currency(client))


        
