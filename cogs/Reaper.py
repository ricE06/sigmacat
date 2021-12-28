import sqlite3
import discord, datetime
from discord.ext import commands, tasks
import datetime
import time
import random
con = sqlite3.connect('reaper.db')
cur = con.cursor()

class Reaper(commands.Cog):
    
    def __init__(self, client: commands.Bot):
        self.client = client

    # MAIN REAPER COMMANDS
    @commands.Cog.listener()
    async def on_message(self, message):
        # tests if the message is valid to run or not
        #valid = (message.channel.id in Reaper.get_channels(self))
        valid = (message.channel.id == 851486147124265000)

        # Reap
        if valid and (message.content == "reap"):
            user_id = message.author.id
            game_id = Reaper.convert(self, message.guild.id)
            print(game_id)
            current_time = int(time.time())
            # Checks if enough time has passed to reap again
            time_since_reap = current_time - int(Reaper.get_user(self, user_id, game_id)[2])
            time_until_reap = 3600 - time_since_reap
            if time_since_reap < 3600: 
                await message.channel.send("You must wait " + str(datetime.timedelta(seconds=time_until_reap)) + " until your next reap.")
            else:
                # Calculates points earned during this reap
                raw_score = current_time - Reaper.get_last_reap(self, game_id)
                multi = Reaper.roll_multiplier(self, user_id, game_id)
                points = round(raw_score * multi)
                # Adds the points to the user's score
                new_total = int(Reaper.get_score(self, user_id, game_id)) + points
                # Checks if this wins the game
                if new_total >= int(Reaper.get_max_score(self, game_id)):
                    await Reaper.end_game(self, message, game_id)
                else:
                    # Adds the points to the player
                    Reaper.update(self, user_id, game_id, new_total, current_time)
                    # Logs the time of the reap, replaces the global last reap time
                    Reaper.update(self, 0, game_id, 0, current_time)
                    # Sends reponse message
                    if multi > 1:
                        # Shortens integer mulipliers to one digit long
                        multi = int(multi) if multi.is_integer() else multi
                        text = "Your reap earned " + str(points)\
                                + " points. You also got a " + str(multi) + "x reap!"
                    else:
                        text = "Your reap earned " + str(points) + " points."
                    await message.channel.send(text)

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
            current_time = int(time.time())
            time_since_reap = current_time - int(Reaper.get_user(self, user_id, game_id)[2])
            time_until_reap = 3600 - time_since_reap
            if time_since_reap < 3600: 
                await message.channel.send("You must wait " + str(datetime.timedelta(seconds=time_until_reap)) + " until your next reap.")
            else:
                await message.channel.send("You can reap right now!")

        # Leaderboard
        if valid and (message.content == "leaderboard"):
            game_id = Reaper.convert(self, message.guild.id)
            # Gets all the scores, in descending order
            cur.execute("SELECT user, score FROM " + game_id + " ORDER BY score DESC")
            full = cur.fetchall()
            # The thing the bot actually displays
            string = "\n"
            for i in range(min(len(full), 10)):
                id = int(full[i][0])
                user = await self.client.fetch_user(id)
                string = string + "\n" + str(user.display_name) + ": `" \
                         + str(full[i][1]) + "`"
            await message.channel.send(string)


    # Begins a new reaper game!
    @commands.command()
    async def start_game(self, ctx:commands.Context, max_points):
        game_id = "game_" + str(ctx.message.guild.id)
        if game_id not in Reaper.get_servers(self):
            channel = ctx.message.channel.id
            current_time = int(time.time())
            Reaper.create_table(self, game_id, channel, max_points, 1, 1, 0, current_time)
            await ctx.send("Game started.")
        else:
            await ctx.send("There is already a game in this server!")

    # Ends the current reaper game.
    async def end_game(self, message, game_id):
        winner = message.author.id
        await message.channel.send("The game has ended. Congratulations to <@" + str(winner) + "> for winning!")
        cur.execute("DROP TABLE " + str(game_id))
        cur.execute("DELETE FROM metadata WHERE server=?", (game_id,))
        con.commit()
        

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

    # Gets the timestamp of the most recent reap from any user
    def get_last_reap(self, game_id):
        cur.execute("SELECT * FROM {} WHERE user=0".format(game_id))
        return cur.fetchone()[2]

    # Gets the full dataset for a user
    def get_user(self, user_id, game_id):
        users = Reaper.get_users(self, game_id)
        if user_id not in users:
            cur.execute("INSERT INTO " + str(game_id) + " VALUES(?, ?, ?, ?, ?)", \
                        (user_id, 0, 0, 0, 1))
            con.commit()
        cur.execute("SELECT * FROM " + str(game_id) + " WHERE user=?", (user_id,))
        return cur.fetchone()

    # Updates the score and last reap time for a user
    def update(self, user_id, game_id, score, time):
        users = Reaper.get_users(self, game_id)
        if user_id in users:
            cur.execute("UPDATE " + str(game_id) + " SET score=?, last_reap=? WHERE user=?", (score, time, user_id))
        else:
            cur.execute("INSERT INTO " + str(game_id) + " VALUES(?, ?, ?, ?, ?)", (user_id, score, time, 0, 1))
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
        cur.execute("CREATE TABLE " + str(game_id) + " (user, score, last_reap, add_multi, multi_multi)")
        cur.execute("INSERT INTO " + str(game_id) + " VALUES(?, ?, ?, ?, ?)", (0, 0, current_time, 0, 0))
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

