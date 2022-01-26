import sqlite3
import discord
from discord.ext import commands, tasks
import datetime
from datetime import date, time
import time
import asyncio


con = sqlite3.connect('greed.db')
cur = con.cursor()

class Greed(commands.Cog, description="Greed control"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.index = 0
    
    # Place your bet!
    @commands.command(help="Place your bets! Syntax: `$greed (number)`")
    async def greed(self, ctx):
        user_id = ctx.message.author.id
        if self.Jail.check_jail(user_id) == True:
            await ctx.send("You can't play greed control in jail!")
            return
        
        max_bet = Greed.get_user(self, 0)[2]
        await ctx.author.send("Pick a number between 1 and " + str(max_bet) + ".")
        channel = ctx.author.dm_channel
        def check(m):
            if m.channel != channel:
                return False
            bet = m.content
            try: 
                bet = int(bet)
            except:
                return False
            if bet < 1 or bet > max_bet:
                return False
            return True
        bet = await self.client.wait_for("message", check=check, timeout=15)
        bet = int(bet.content)        
        previous = Greed.get_user(self, user_id)[2]
        cur.execute("UPDATE scores SET bet=? WHERE user=?", (bet, user_id))
        con.commit()
        if previous == 0:
            await channel.send("Successfully picked " + str(bet) + "!")
        else:
            await channel.send("Successfully updated the bet to " + str(bet) + "!")

    # Displays the current greed control score
    @commands.command(name="points_greed", help="Displays your current point total.")
    async def show_current(self, ctx):
        channel = ctx.message.channel
        user_id = ctx.message.author.id 
        points = self.get_user(user_id)[1]
        await channel.send("You currently have " + str(points) + " points in Greed Control.")

    # Displays a top 10 leaderboard in greed control
    @commands.command(name="greederboard", help="Displays the top 10 point scores in greed control.")
    async def leaderboard(self, ctx):
        channel = ctx.message.channel
        cur.execute("SELECT user, score FROM scores ORDER BY score DESC")
        winners = cur.fetchmany(11)
        del winners[0]
        max_score = float(self.get_user(0)[1])
        string = "Greed control leaderboard. The score required to win is: " + str(max_score)
        for i in range(len(winners)):
            user_id = int(winners[i][0])
            user = await self.client.fetch_user(user_id)
            name = user.display_name
            string = string + "\n" + str(name) + ": `" \
                     + str(winners[i][1]) + "`"
        await channel.send(string)



    # Scuffed function to get a function to run at midnight each day, obsolete
    @commands.command()
    async def timer(self, ctx):
        if ctx.message.author.id != 732415222706339840:
            return
        while True:
            current = time.ctime()
            seconds = int(current[17:19])
            minutes = int(current[14:16])
            hours = int(current[11:13])
            wait = (23 - hours)*3600 + (59-minutes)*60 + seconds
            if wait == 0:
                wait = 86400
            print(wait)
            await asyncio.sleep(wait)
            await self.give_points()
            await asyncio.sleep(30)
            

    # Distributes points every 24 hours
    async def give_points(self):
        channel_id = 928099803768950834
        channel = await self.client.fetch_channel(channel_id)
        max_bet = int(self.get_user(0)[2])
        max_score = int(self.get_user(0)[1])
        print(max_score)

        # Creates list showing how often each number was picked
        freq = []
        for i in range(max_bet):
            freq.append(0)

        scores = self.get_full()
        string = "Points awarded: "
        del scores[0]
        for user in scores:
            pick = user[2]
            if pick != 0:
                freq[pick-1] += 1
        print(freq)

        string = "Distribution of numbers: "
        for i in range(max_bet):
            string += "\n" + str(i+1) + ": " + str(freq[i])
        await channel.send(string)

        # Creates list showing points awarded for each number
        points = []
        for i in range(len(freq)):
            if freq[i] == 0:
                points.append(0)
            else:
                points.append(round(int(i+1) / freq[i], 4))
        print(points)

        winners = []
        for user in scores:
            user_id = user[0]
            if user[2] > 0:
                earned = points[user[2]-1]
                new_score = round(user[1] + earned, 4)
                if new_score >= max_score:
                    winners.append(user_id)
                cur.execute("UPDATE scores SET score=?, bet=? WHERE user=?", (new_score, 0, user_id))

        if len(winners) >= 1:
            if len(winners) == 1:
                await channel.send("<@" + str(winners[0]) + "> has won the game!")
            else:
                string = "Winners: "
                for user_id in winners:
                    string += "\n<@" + str(user_id) + ">"
                await channel.send(string)
            await self.end()
        con.commit()

    # test function
    # @commands.command()
    # async def test(self, ctx):
    #     await Greed.printer(self)


    # Makes a new reaper game (this game is global)
    @commands.command(help="Begins a new Greed Control game. Note that only specified developers can use this command.")
    async def new_greed(self, ctx, max_points, max_bet):
        if ctx.message.author.id != 732415222706339840:
            await ctx.message.channel.send("You cannot use this command!")
            return
        cur.execute("DROP TABLE IF EXISTS scores")  
        cur.execute("CREATE TABLE IF NOT EXISTS scores (user INTEGER, score REAL, bet INTEGER)")
        cur.execute("INSERT INTO scores VALUES (?, ?, ?)", (0, max_points, max_bet))
        con.commit()
        await ctx.message.channel.send("Successfully begun a new Greed Control game.")

    # Deletes the previous greed control table
    @commands.command(help="Ends the current Greed Control game. Note that only specified developers can use this command.")
    async def end_greed(self, ctx):
        if ctx.message.author.id != 732415222706339840:
            await ctx.message.channel.send("You cannot use this command!")
            return
        await self.end()
        await ctx.message.channel.send("Successfully ended the current Greed Control game.")   

    async def end(self):
        cur.execute("DROP TABLE IF EXISTS scores")  
        con.commit()
       
                 
    # Gets the score and bet for a user
    def get_user(self, user_id):
        cur.execute("SELECT * FROM scores WHERE user=?", (user_id,))
        data = cur.fetchone()
        if data is None:
            cur.execute("INSERT INTO scores VALUES (?, ?, ?)", (user_id, 0, 0))
            return (user_id, 0, 0)
        else:
            return data 

    def get_full(self):
        cur.execute("SELECT * FROM scores")
        rows = cur.fetchall()
        return rows    
    
def setup(client):
    client.add_cog(Greed(client))
