import sqlite3
import discord
from discord.ext import commands, tasks
from datetime import date

con = sqlite3.connect('greed.db')
cur = con.cursor()

class Greed(commands.Cog, description="Greed control"):
    def __init__(self, client: commands.Bot):
        self.client = client
    
	# Place your bet!
	@commands.Command(help="Place your bets! Syntax: `$greed (number)`")
	async def greed(self, ctx, bet):
		channel = ctx.message.channel
		max_bet = Greed.get_user(self, 0)[2]
		try: 
			bet = int(bet)
		else:
			await channel.send("Please pick a number!")
		if bet < 1 or bet > max_bet:
			await channel.send("Your bet is out of range!")
			return
		user_id = ctx.message.author.id
		previous = Greed.get_user(self, user_id)[2]
		cur.execute("UPDATE scores SET bet=? WHERE user=?", (bet, user_id))
		con.commit()
		if previous == 0:
			await channel.send("Successfully picked " + str(bet) + "!")
		else:
			await channel.send("Successfully updated the bet to " + str(bet) + "!")
	
    # Deletes old table, makes a new one (this game is global)
	@commands.Command(help="Begins a new Greed Control game. Note that only specified developers can use this command.)
    async def new_greed(self, ctx, max_points, max_bet):
		if ctx.message.author != 732415222706339840:
			await ctx.message.channel.send("You cannot use this command!")
			return
        cur.execute("DROP TABLE IF EXISTS scores")
        cur.execute("CREATE TABLE IF NOT EXISTS scores (user INTEGER, score REAL, bet INTEGER)")
        cur.execute("INSERT INTO scores VALUES (?, ?, ?)", (0, max_points, max_bet)
        con.commit()
		await ctx.message.channel.send("Successfully begun a new Greed Control game.")
					
	# Gets the score and bet for a user
    def get_user(self, user_id):
		cur.execute("SELECT * FROM scores WHERE user=?", (user_id,))
		data = cur.fetchone()
		if data is None:
			cur.execute("INSERT INTO scores VALUES (?, ?, ?)", (user_id, 0, 0))
			return (user_id, 0, 0)
		else:
			return data		
	
def setup(client):
    client.add_cog(Greed(client))
