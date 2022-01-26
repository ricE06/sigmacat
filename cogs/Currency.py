import sqlite3
import discord
from discord.ext import commands, tasks
from datetime import date
import time
import math
import random
con = sqlite3.connect('currencies.db')
cur = con.cursor()

interest_rates = [1, 1.001, 1.0025, 1.005, 1.01, 1.015, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09, 1.1]

# noinspection PyUnresolvedReferences
class Currency(commands.Cog, description="o-bucks"):
    """
    o-bucks
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.Jail = self.client.get_cog("Jail")
        print(self.Jail)

    @commands.command(name="balance", help="Displays the current balance of a user\nSyntax: `$balance` or `$balance @user`")
    async def show_balance(self, ctx, usr: discord.Member=None):
        if usr is None:
            usr = ctx.author

        wallet = self.get_current(usr.id)
        bank = self.get_bank_current(usr.id)
        cur.execute("SELECT interest FROM bank WHERE user=?", (usr.id,))
        bank_interest = cur.fetchone()
        if bank_interest is None:
            bank_interest = 0
        else:
            bank_interest = bank_interest[0]
        bank_interest = str(bank_interest) + "%"
        net_worth = wallet + bank
        net_worth_rank = self.calc_currency_rank(usr.id)
        jailed = self.Jail.check_jail(usr.id)
        collected_daily = self.collected_daily(usr.id)
        daily_value = self.get_current(0)
        stealing = self.calc_steal_value(usr.id)


        emb=discord.Embed()
        emb.set_author(name=usr, icon_url=usr.avatar_url)
        emb.add_field(name="Wallet", value=str(wallet), inline=True)
        emb.add_field(name="Net worth", value=str(net_worth), inline=True)
        emb.add_field(name="Net worth rank", value=str(net_worth_rank), inline=True)
        emb.add_field(name="Bank account", value=str(bank), inline=True)
        emb.add_field(name="Bank interest", value=str(bank_interest), inline=True)
        emb.add_field(name="Stealing", value=str(stealing), inline=True)
        emb.add_field(name="Jailed", value=str(jailed), inline=True)
        emb.add_field(name="Collected daily", value=str(collected_daily), inline=True)
        emb.add_field(name="Daily value", value=str(daily_value), inline=True)
        emb.set_footer(text="Developed by ricez cakes#3813")
        await ctx.send(embed=emb)


        await ctx.send(usr.name + " currently has " + str(Currency.get_current(self, usr.id)) + " O-bucks and " + str(self.get_bank_current(usr.id)) + " in the bank.")

    @commands.command(name="daily", help="Adds 1000 to a user if they have not used this command within the last 24 hours. Syntax: `$daily`")
    async def give_daily(self, ctx:commands.Context):
        user_id = ctx.message.author.id
        if self.Jail.check_jail(user_id) == True:
            await ctx.send("You can't collect a daily while in jail!")
            return
        last_daily = Currency.get_last_daily(self, user_id)
        current_date = str(date.today())
        daily_amount = int(self.get_current(0))
        if last_daily == current_date:
            await ctx.send("You've already collected your daily today you greedy piece of shit!")
        else:
            new = Currency.get_current(self, user_id) + daily_amount
            Currency.update(self, user_id, new)
            cur.execute("UPDATE balances SET lastDaily=? WHERE user=?", (str(current_date), user_id))
            con.commit()
            await ctx.send("Successfully deposited " + str(daily_amount) + " O-bucks!")

    # Checks if a user has collected their daily
    def collected_daily(self, user_id):
        return True

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
        
        # sigmacat ID 922586734057889792
        # deltacat ID 797986816418119721
        if receiver == 797986816418119721 and bal >= 100:
            daily_change = math.floor(bal / 100)
            self.change(0, daily_change)
            await ctx.send("Thank you for your generous donation. As thanks, the daily income has been permanently increased by " + str(daily_change) + " O-bucks for everyone.")

    # Begins the stealing process
    @commands.command(help="Steal from another user. After 12 hours, you will steadily siphon their money until you `$escape` and leave with the money that you have collected thus far. After 48 hours, all the money will be ready to collect, but you can continue earning until 72 hours.")
    async def steal(self, ctx, user: discord.Member):
        user_id = ctx.message.author.id
        is_stealing = self.check_stealing(user_id)
        if not is_stealing:
            await ctx.send("Currently stealing from <@" + str(user.id) + ">!")
        else:
            await ctx.send("You can't steal from multiple people simultaneously! Use `$escape` to leave the current heist.")
            return
        current_time = int(time.time())
        amount = self.get_current(user.id)
        cur.execute("INSERT INTO theft VALUES(?, ?, ?, ?)", (user_id, user.id, current_time, amount))
        con.commit()


    # Stores the stolen money
    @commands.command(help="Escapes with your newly stolen money!")
    async def escape(self, ctx):
        user_id = ctx.message.author.id
        if not self.check_stealing(user_id):
            await ctx.send("As you're not stealing from anyone right now, the only thing you've escaped from is your responsibilities.")
            return
        stolen_amount = self.calc_steal_value(user_id)
        if stolen_amount == 0:
            await ctx.send("You must wait at least 12 hours before you can steal anything!")
            return
        cur.execute("SELECT * FROM theft WHERE stealer=?", (user_id,))
        stealed = cur.fetchone()[1]
        self.change(user_id, stolen_amount)
        self.change(stealed, -stolen_amount)
        cur.execute("DELETE FROM theft WHERE stealer=?", (user_id,))
        con.commit()
        await ctx.send("Successfully secured " + str(stolen_amount) + " O-bucks!")

    # Displays the amount to be earned
    @commands.command(help="Displays the current amount you would walk away with if you retreat from your heist.")
    async def steal_status(self, ctx):
        user_id = ctx.message.author.id
        if not self.check_stealing(user_id):
            await ctx.send("You aren't stealing from anyone!")
            return
        value = self.calc_steal_value(user_id)
        if value == 0:
            await ctx.send("You must wait at least 12 hours before you can steal anything!")
            return
        else:
            await ctx.send("Your current steal value is " + str(value) + " O-bucks.")  

    # Checks if the user is currently stealing
    def check_stealing(self, user_id):
        cur.execute("SELECT * FROM theft WHERE stealer=?", (user_id,))
        if cur.fetchone() == None:
            return False
        else:
            return True    

    # Calculates the amount earned
    def calc_steal_value(self, user_id):
        cur.execute("SELECT * FROM theft WHERE stealer=?", (user_id,))
        row = cur.fetchone()
        if row is None:
            return 0
        stealed = row[1]
        steal_time = int(row[2])
        total_amount = row[3]
        current_time = int(time.time())
        difference = current_time - steal_time
        if difference <= 432:
            difference = 432
        elif difference > 2592:
            difference = 2592
        stolen_amount = round((difference - 432)*total_amount/1296)
        return stolen_amount

    # Catches the user if they are stealing from you, you lose 1000 o-bucks if not
    @commands.command(help="Catch all the users that are currently siphoning money from you.")
    async def catch(self, ctx):
        user_id = ctx.message.author.id
        filtered = cur.execute("SELECT * FROM theft WHERE stealed=?", (user_id,))
        jail_num = 0
        for row in filtered:
            self.Jail.jail(row[0], 43200)
            jail_num += 1

        if jail_num == 0:
            ctx.send("No one is stealing from you! You got fined 2000 O-bucks for wasting the police's time.")
            return

        string = "Successfully jailed " + str(jail_num) + " user"
        if jail_num != 1:
            string += "s"
        string += "!"
        await ctx.send(string)

    # Deposits into the bank
    @commands.command(help="Deposit your O-bucks into your bank!")
    async def deposit(self, ctx, amount):
        user_id = ctx.message.author.id
        channel = ctx.message.channel
        if str(amount) == "all":
            amount = self.get_current(user_id)
        try:
            amount = int(amount)
        except:
            await channel.send("You must input a valid integer to deposit!")
            return
        if amount > int(self.get_current(user_id)):
            await channel.send("tomorrow our debt collectors will come knocking on your door... oh wait they're already here")
            return
        elif amount == 0:
            await channel.send("why are you even here")
            return
        elif amount < 0:
            await channel.send("The teller takes one look at your counterfeit bills with minus signs scribbled on them, laughs in your face, and calls security.")
            return
        user_id = ctx.message.author.id
        old_balance = int(self.get_bank_current(user_id))
        try:
            cur.execute("UPDATE bank SET balance=? WHERE user=?", (old_balance + amount, user_id))
        except:
            cur.execute("INSERT INTO bank VALUES (?, ?, ?)", (user_id, amount, 0))
        con.commit()
        self.change(user_id, -amount)
        await ctx.message.channel.send("Successfully deposited " + str(amount) + " O-bucks into your bank account!")

    # Meant to run every 24 hours. Tasks:
    # - go through every entry and add the interest
    # - update the interest to a larger amount if it isn't 10%, if it is, then it keeps it there
    #@commands.command()
    async def bank_update(self):
        cur.execute("SELECT * FROM bank")
        bank_table = cur.fetchall()
        for row in bank_table:
            rate_index = int(row[2])
            if rate_index > 14:
                rate_index = 14
            interest_rate = interest_rates[rate_index]
            new_bank_balance = math.floor(row[1] * interest_rate)
            cur.execute("UPDATE bank SET interest=?, balance=? WHERE user=?", (row[2]+1, new_bank_balance, row[0]))
        con.commit()

    # Admin only command 
    @commands.command(help="Only specified developers can use to set someone's balance.")
    async def set(self, ctx, user: discord.Member, bal):
        if ctx.message.author.id != 732415222706339840:
            await ctx.message.channel.send("You can't use this!")
            return
        try:
            bal = int(bal)
        except:
            await ctx.message.channel.send("Must be an integer!")
            return
        self.update(user.id, bal)
        await ctx.message.channel.send("Successfully set balance to " + str(bal) + " O-bucks!")
            
    # Withdraws money, resets interest rate
    @commands.command(help="Withdraws all your moneyf rom your bank account. Note that your interest rate will reset and you will have to wait the full 14 days to get it back up to the maximum amount.")
    async def withdraw(self, ctx):
        user_id = ctx.message.author.id 
        bank_balance = self.get_bank_current(user_id)
        cur.execute("UPDATE bank SET interest=?, balance=? WHERE user=?", (0, 0, user_id))
        con.commit()
        self.change(user_id, bank_balance)
        await ctx.send("Successfully withdrew " + str(bank_balance) + " O-bucks!")

    @commands.command(name="interest", help="Displays your current interest rate.")
    async def show_interest(self, ctx):
        user_id = ctx.message.author.id
        channel = ctx.message.channel

        if self.get_bank_current(user_id) == 0:
            await channel.send("You have nothing in the bank!")
            return

        cur.execute("SELECT * FROM bank WHERE user=?", (user_id,))
        rate = int(cur.fetchone()[2])
        if rate > 14:
            rate = 14
        percent = round((interest_rates[rate]) * 100 - 100, 5)
        await channel.send("Your current interest rate is " + str(percent) + "% per day.")

    # goddamnit you millenials living on government handouts
    @commands.command(help="Gives you one O-buck if you have none left.")
    async def welfare(self, ctx):
        user_id = ctx.message.author.id
        if self.get_current(user_id) == 0:
            self.update_balance(user_id, 1)
            await ctx.message.channel.send("Successfully set your O-bucks to 1!")
        else:
            await ctx.message.channel.send("Stop looking for handouts you greedy bastard!")

    # Displays the current daily value
    @commands.command(name="daily_value", help="Displays the current value of the daily.")
    async def show_daily_value(self, ctx):
        channel = ctx.message.channel
        await ctx.message.channel.send("The current daily value is " + str(self.get_current(0)) + " O-bucks!")

    # Calculates the rank you are in total wealth
    def calc_currency_rank(self, user_id):
        return 0
        cur.execute("SELECT user, amount, ")

    # Displays the leaderboard of wealth
    @commands.command(name="forbeslist", help="Displays the ten wealthiest people.")
    async def currency_leaderboard(self, ctx):
        async ctx.send("under development")
        return
        cur.execute("SELECT user, amount FROM balances")
        balances = cur.fetchall()
        
        for user_id in self.get_users():
            print(user_id)
            net_worth = self.get_net_worth(user_id)
            try:
                user = await self.client.fetch_user(user_id)
            except:
                print("invalid user")
            else:
                full_list[user.display_name] = net_worth
        print("thonk")
        string="Top 10 wealthiest users: "
        for name in full_list:
            string = string + "\n" + str(name) + ": `" + str(full_list[name]) + "`"
        await ctx.send(string)


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

    # Gets the current bank balance of a user
    def get_bank_current(self, user_id):
        cur.execute("SELECT * FROM bank WHERE user=?", (user_id,))
        row = cur.fetchone()
        if row == None:
            return 0
        else:
            return row[1]        

    # Gets the net worth of a user
    def get_net_worth(self, user_id):
        return self.get_current(user_id) + self.get_bank_current(user_id)

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
    global Jai    


        
