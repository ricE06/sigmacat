import discord
from discord.ext import commands
import random

class Landlord(commands.Cog, description="Landlord and Peasant is a traditional Chinese card game for three players."):
	"""
	lol
	"""
    
	def __init__(self, client: commands.Bot):
		self.client = client


def setup(client):
    client.add_cog(Landlord(client))