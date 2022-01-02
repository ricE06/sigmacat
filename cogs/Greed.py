import sqlite3
import discord
from discord.ext import commands, tasks
from datetime import date

class Greed(commands.Cog, description="Greed control"):
    def __init__(self, client: commands.Bot):
        self.client = client	

def setup(client):
    client.add_cog(Greed(client))