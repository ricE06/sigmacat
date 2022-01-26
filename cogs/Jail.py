import sqlite3
import discord
from discord.ext import commands, tasks
import time
import datetime
import random

con = sqlite3.connect('jail.db')
cur = con.cursor()

class Jail(commands.Cog, description="do not pass go."):
	"""
	do not pass go
	"""

	def __init__(self, client: commands.Bot):
		self.client = client

	# Checks if a user is in jail
	def check_jail(self, user_id):
		cur.execute("SELECT * FROM jail WHERE user_id=?", (user_id,))
		row = cur.fetchone()
		if row == None:
			return False
		else:
			return True

	# Throws the user in jail (duration in seconds)
	def jail(self, user_id, duration):
		if self.check_jail(user_id):
			cur.execute("DELETE FROM jail WHERE user_id=?", (user_id,))
		release_time = int(time.time()) + int(duration)
		cur.execute("INSERT INTO jail VALUES (?, ?)", (user_id, release_time))
		con.commit()

	# Manually jails a person
	@commands.command(name="jail", help="Manually throws a user in jail. Can only be used by specified developers.")
	async def jail_manual(self, ctx, user: discord.Member, duration):
		if ctx.message.author.id != 732415222706339840:
			ctx.send("You can't use this!")
			return
		try:
			duration = int(duration)
		except:
			ctx.send("Remember, the duration is in seconds and must be an integer!")
			return
		self.jail(user.id, duration)
		await ctx.send("Successfully jailed <@" + str(user.id) + "> for " + str(duration) + " seconds.")

	# Get out of jail
	@commands.command(name="unjail", help="Gets you out of jail, or manually overrides the jail if used by a developer.")
	async def unjail(self, ctx, user: discord.Member=None):
		override = ctx.message.author.id == 732415222706339840
		if user is None or not override:
			user = ctx.author
		
		# 1% chance of breaking out
		lol = random.randint(1, 100)
		if lol == 1:
			override = True

		if not override:
			cur.execute("SELECT release_time FROM jail WHERE user_id=?", (user.id,))
			release_time = int(cur.fetchone()[0])
			current_time = int(time.time())
			difference = release_time - current_time
			if difference > 0:
				await ctx.send("You must wait " + str(datetime.timedelta(seconds=difference)) + " before you can get of jail.")
				return

		cur.execute("DELETE FROM jail WHERE user_id=?", (user.id,))
		con.commit()
		if lol != 1:
			await ctx.send("Successfully released from jail!")
		else:
			await ctx.send("Successfully broke out of jail!")






def setup(client):
    client.add_cog(Jail(client))