import sqlite3
import discord, datetime
from discord.ext import commands, tasks
from datetime import date
import time
import random
import math
con = sqlite3.connect('reaper.db')
cur = con.cursor()

class Reaper(commands.Cog, description="Reaper is a patience game"):
    """
    Reap by typing `reap`. The amount of points you can get from a single reap \
    is the exact number of seconds since the previous person reaped. The winner \
    is the first to a set amount of points. \
    Other commands can be found in the channel description.\n\
    Some reaper games can be *monetized*, meaning that you must pay a certain number \
    of O-bucks to reap in them. The O-bucks remain in a prize pool until the game \
    *is played to completion*, when they will be distributed among the players \
    based on their scores and a couple other additional factors (such as ranking).
    """
    def __init__(self, client: commands.Bot):
        self.client = client
        self.Jail = self.client.get_cog("Jail")

    # MAIN REAPER COMMANDS
    @commands.Cog.listener()
    async def on_message(self, message):
        # tests if the message is valid to run or not
        valid = (message.channel.id in Reaper.get_channels(self)) and (self.Jail.check_jail(user_id) == False)
        #valid = (message.channel.id == 851486147124265000)

        # Reap
        if valid and (message.content == "reap"):
            user_id = message.author.id
            game_id = Reaper.convert(self, message.guild.id)
            reap_cost = int(Reaper.get_user(self, user_id, game_id)[5])
            user_balance = Currency.get_current(user_id)
            current_time = int(time.time())
            # Checks if enough time has passed to reap again (only if monetize is off)
            time_since_reap = current_time - int(Reaper.get_user(self, user_id, game_id)[2])
            time_until_reap = 3600 - time_since_reap
            if time_since_reap < 3600 and Reaper.get_single_metadata(self, game_id)[5] == 0:
                await message.channel.send("You must wait " + str(datetime.timedelta(seconds=time_until_reap)) + " until your next reap.")
            # Checks if the user has enough O-bucks to reap
            elif user_balance < reap_cost:
                string = "You don't have enough O-bucks to reap!"
                # Checks if daily is avaliable
                last_daily = Currency.get_last_daily(user_id)
                current_date = str(date.today())
                if last_daily != current_date:
                    string += " However, you do have 1000 O-bucks avaliable by using `$daily`."
                await message.channel.send(string)
            else:
                # Calculates points earned during this reap
                raw_time = current_time - Reaper.get_last_reap(self, game_id)
                raw_score = Reaper.tapering(self, raw_time)
                multi = Reaper.roll_multiplier(self, user_id, game_id)
                points = round(raw_score * multi)
                # Adds the points to the user's score
                new_total = int(Reaper.get_score(self, user_id, game_id)) + points
                # Spends the O-bucks
                Currency.change(user_id, -reap_cost)
                # Adds the points to the player and the total
                new_cost = round(reap_cost * 1.05)
                Reaper.update(self, user_id, game_id, new_total, current_time, new_cost)
                previous_total = int(Reaper.get_user(self, 0, game_id)[1])
                # Logs the time of the reap, replaces the global last reap time
                pool = int(Reaper.get_user(self, 0, game_id)[5])
                new_pool = pool + reap_cost
                Reaper.update(self, 0, game_id, previous_total + points, current_time, new_pool)
                # O-bucks earned for reaping
                if points > 1000 and Reaper.get_single_metadata(self, game_id)[5] == 1:
                    bonus = round((raw_score - 1500) / 25)
                    Currency.change(user_id, bonus)
                else:
                    bonus = 0
                # Sends reponse message
                text = "Your reap time was " + str(raw_time) + " seconds, earning " + str(points) + " points."
                if multi > 1:
                    # Shortens integer mulipliers to one digit long
                    multi = int(multi) if multi.is_integer() else multi
                    text += " You also got a " + str(multi) + "x reap!"
                if bonus > 0:
                    text += " In addition, you earned " + str(bonus) + " O-bucks!"
                await message.channel.send(text)
                # Checks if this wins the game
                if new_total >= int(Reaper.get_max_score(self, game_id)):
                    await Reaper.reward(self, game_id, message.channel)
                    await Reaper.end(self, message, game_id)

        # Rank
        if valid and (message.content == "rank"):
            user_id = message.author.id
            game_id = Reaper.convert(self, message.guild.id)
            await message.channel.send("Your current score is " + \
                                       str(Reaper.get_score(self, user_id, game_id)) + " points.")
        # Timer
        if valid and (message.content == "timer"):
            game_id = Reaper.convert(self, message.guild.id)
            current_time = int(time.time())
            points = current_time - int(Reaper.get_last_reap(self, game_id))
            await message.channel.send("The current reap time is " + str(points) + " seconds.")

        # Nextreap
        if valid and (message.content == "nextreap"):
            user_id = message.author.id
            game_id = Reaper.convert(self, message.guild.id)
            if Reaper.get_single_metadata(self, game_id)[5] == 0:
                current_time = int(time.time())
                time_since_reap = current_time - int(Reaper.get_user(self, user_id, game_id)[2])
                time_until_reap = 3600 - time_since_reap
                if time_since_reap < 3600: 
                    await message.channel.send("You must wait " + str(datetime.timedelta(seconds=time_until_reap)) + " until your next reap.")
                else:
                    await message.channel.send("You can reap right now!")
            else:
                await message.channel.send("There is no wait period in this game!")

        # Leaderboard
        if valid and (message.content == "leaderboard"):
            game_id = Reaper.convert(self, message.guild.id)
            # Gets all the scores, in descending order
            cur.execute("SELECT user, score FROM " + game_id + " ORDER BY score DESC")
            winners = cur.fetchmany(11)
            del winners[0]
            # The thing the bot actually displays
            max_score = int(Reaper.get_single_metadata(self, game_id)[2])
            string = "Reaper leaderboard. The score required to win is: " + str(max_score)
            for i in range(len(winners)):
                user_id = int(winners[i][0])
                try:
                    user = message.guild.get_member(user_id)
                    name = user.nick
                except:
                    name = "[user not found]"
                if str(name) == "None":
                    user = await self.client.fetch_user(user_id)
                    name = user.display_name
                string = string + "\n" + str(name) + ": `" \
                         + str(winners[i][1]) + "`"
            await message.channel.send(string)

        # Cost
        if valid and (message.content == "cost"):
            user_id = message.author.id
            game_id = Reaper.convert(self, message.guild.id)
            if Reaper.get_single_metadata(self, game_id)[5] == 1:
                cost = str(Reaper.get_user(self, user_id, game_id)[5])
                await message.channel.send("Your current reap cost is " + cost + " O-bucks.")
            else:
                await message.channel.send("Reaping in this game is free!")

        # Pool
        if valid and (message.content == "pool"):
            game_id = Reaper.convert(self, message.guild.id)
            if Reaper.get_single_metadata(self, game_id)[5] == 1:
                pool = str(Reaper.get_user(self, 0, game_id)[5])
                await message.channel.send("There are currently " + pool + " O-bucks up for grabs.")
            else:
                await message.channel.send("There are no rewards in this game!")


    # Begins a new reaper game!
    @commands.command(help="Begin a new reaper game.\nNote that only admins may begin a game.\nSyntax: `$start_game [max_points]`")
    @commands.has_permissions(administrator=True)
    async def start_game(self, ctx:commands.Context, max_points):
        game_id = "game_" + str(ctx.message.guild.id)
        if game_id not in Reaper.get_servers(self):
            channel = ctx.message.channel.id
            current_time = int(time.time())
            Reaper.create_table(self, game_id, channel, max_points, 1, 1, 1, current_time)
            await ctx.send("Game started.")
        else:
            await ctx.send("There is already a game in this server!")

    # Ends the current reaper game.
    async def end(self, message, game_id):
        winner = message.author.id
        await message.channel.send("The game has ended. Congratulations to <@" + str(winner) + "> for winning!")
        cur.execute("DROP TABLE " + str(game_id))
        cur.execute("DELETE FROM metadata WHERE server=?", (game_id,))
        con.commit()

    # End game command    
    @commands.command(help="Ends the current reaper game.\nNote that only admins may end a game\nSyntax: `$end_game`")
    @commands.has_permissions(administrator=True)
    async def end_game(self, ctx:commands.Context):
        game_id = Reaper.convert(self, ctx.message.guild.id)
        message = ctx.message
        await Reaper.end(self, message, game_id)

    # Calculates raw points earned using tapering function
    def tapering(self, time):
        return (4800*math.atan(time/6000) + (time/5))


    # Distributes O-bucks at the end of a game
    async def reward(self, game_id, channel):
        # Gets the top ten, in descending order
        cur.execute("SELECT user, score FROM " + game_id + " ORDER BY score DESC")
        winners = cur.fetchmany(11)
        max_score = int(Reaper.get_single_metadata(self, game_id)[2])
        del winners[0]
        if Reaper.get_single_metadata(self, game_id)[5] == 1 and \
        max_score >= 25000 and len(winners) >= 5:
            pool = Reaper.get_user(self, 0, game_id)[5]
            total_score = Reaper.get_user(self, 0, game_id)[1]
            string = "O-bucks awarded: "
            for i in range(len(winners)):
                if i < 3:
                    multi = 1.5
                elif i >= 3 and i < 5:
                    multi = 1.2
                elif i>= 5 and i < 10:
                    multi = 1 
                else:
                    multi = 0
                user_id = winners[i][0]
                score = int(winners[i][1])
                amount_won = round(multi * pool * (score / total_score))
                if i==0 and score > max_score:
                    amount_won += round((score - max_score)/5)
                Currency.change(user_id, amount_won)
                try:
                    user = await self.client.fetch_user(user_id)
                    name = user.display_name
                except:
                    name = "[user not found]"
                string = string + "\n" + str(name) + ": `" \
                         + str(amount_won) + "`"
            await channel.send(string)
        else:
            if len(winners) < 10:
                await channel.send("There are not enough people playing to award O-bucks.")
            elif Reaper.get_single_metadata(self, game_id)[2] < 50000:
                await channel.send("The max score must be at least 50k to award O-bucks.")
            else:
                await channel.send("No O-bucks were awarded because the game was not monetized.")



    # Gets the current score of a user
    def get_score(self, user_id, game_id):
        users = Reaper.get_users(self, game_id)
        if user_id in users:
            cur.execute("SELECT * FROM " + str(game_id) + " WHERE user=?", (user_id,))
            return cur.fetchone()[1]
        else:
            return 0

    # Gets the required score to win
    def get_max_score(self, game_id):
        cur.execute("SELECT * FROM metadata WHERE server=?", (game_id,))
        return cur.fetchone()[2]

    # Gets the metadata for one game
    def get_single_metadata(self, game_id):
        cur.execute("SELECT * FROM metadata WHERE server=?", (game_id,))
        return cur.fetchone()

    # Gets the timestamp of the most recent reap from any user
    def get_last_reap(self, game_id):
        cur.execute("SELECT * FROM {} WHERE user=0".format(game_id))
        return cur.fetchone()[2]

    # Gets the full dataset for a user
    def get_user(self, user_id, game_id):
        users = Reaper.get_users(self, game_id)
        if user_id not in users:
            Reaper.update(self, user_id, game_id, 0, 0, 0)
        cur.execute("SELECT * FROM " + str(game_id) + " WHERE user=?", (user_id,))
        return cur.fetchone()

    # Updates the score and last reap time for a user
    def update(self, user_id, game_id, score, time, new_cost):
        users = Reaper.get_users(self, game_id)
        if user_id in users:
            cur.execute("UPDATE " + str(game_id) + \
                        " SET score=?, last_reap=?, cost=? WHERE user=?", \
                        (score, time, new_cost, user_id))
        else:
            if Reaper.get_single_metadata(self, game_id)[5]==1:
                cost = 100
            else:
                cost = 0
            cur.execute("INSERT INTO " + str(game_id) + " VALUES(?, ?, ?, ?, ?, ?)", (user_id, score, time, 0, 1, cost))
        con.commit()

    # Rolls for a multipler. There are three components that go into a multipler:
    # natural, additive, and multiplicative. The formula for the total multiplier
    # is (nat + add) * mult. The formula for calculating the natural multiplier
    # is a geometric distribution with an adjustable probability.
    def roll_multiplier(self, user_id, game_id):
        nat_multi = 1
        roll = random.randint(0, 3)
        if roll == 0:
            nat_multi += 1
            while True:
                flip = random.randint(0, 1)
                if flip > 0:
                    nat_multi += 0.5
                else:
                    break
        add_multi = float(Reaper.get_user(self, user_id, game_id)[3])
        multi_multi = float(Reaper.get_user(self, user_id, game_id)[4])
        multi = round(float((nat_multi + add_multi)*multi_multi), 1)
        return multi

    # Creates a table for a game
    def create_table(self, game_id, channel, max_score, rng, multi, monetize, current_time):
        cur.execute("CREATE TABLE " + str(game_id) + " (user, score, last_reap, add_multi, multi_multi, cost)")
        cur.execute("INSERT INTO " + str(game_id) + " VALUES(?, ?, ?, ?, ?, ?)", (0, 0, current_time, 0, 0, 0))
        cur.execute("INSERT INTO metadata VALUES(?, ?, ?, ?, ?, ?)", \
                    (game_id, channel, max_score, rng, multi, monetize))
        con.commit()

    # Converts "x" to "game_x"
    def convert(self, server_id):
        game_id = "game_" + str(server_id)
        return game_id

    # Returns a list of all servers with active games
    def get_servers(self):
        rows = Reaper.get_metadata(self)
        servers = []
        for row in rows:
            servers.append(row[0])
        return servers

    # Returns a list of all designated reaper games
    def get_channels(self):
        rows = Reaper.get_metadata(self)
        channels = []
        for row in rows:
            channels.append(row[1])
        return channels

    # Returns a list of all users in a game
    def get_users(self, game_id):
        if game_id in Reaper.get_servers(self):
            rows = Reaper.get_full_scores(self, game_id)
            users = []
            for row in rows:
                users.append(row[0])
            return users
        else:
            return []

    # Returns the entire metadata table
    def get_metadata(self):
        cur.execute("SELECT * FROM metadata")
        rows = cur.fetchall()
        return rows

    # Returns the entire table of scores from a game
    def get_full_scores(self, game_id):
        cur.execute('SELECT * FROM {}'.format(game_id))
        rows = cur.fetchall()
        return rows


def setup(client):
    client.add_cog(Reaper(client))
    print("Initialized")
    global Currency
    Currency = client.get_cog("Currency")

