import discord
from discord.ext import commands 
import random

class Five(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.games = {}

    @commands.command()
    async def five(self, ctx):
        if str(ctx.channel.id) in self.games:
            await ctx.send("There is already an active game here!")
            return 

        game = {}

        game["GRID_SIZE"] = 5 
        game["GRID_AREA"] = game["GRID_SIZE"] * game["GRID_SIZE"]
        game["CARD_POOL"] = 10
        game["CARD_REPEAT"] = 4 
        game["IN_PROGRESS"] = False
        game["CURRENT_CARD_COUNT"] = 0
        game["CURRENT_CARD"] = -1
        game["CURRENT_WAITING"] = []

        game["numbers"] = {} 
        game["cards"] = [] 
        game["players"] = []

        await ctx.send("Game starting. Please `join`, `start`, or begin a quick `small` game.")

        self.games[str(ctx.channel.id)] = game

    @commands.command()
    async def fjoin(self, ctx):
        lId = str(ctx.channel.id)

        if lId not in self.games:
            await ctx.send("There is no active game in this channel. \
You can use `$five` to start one!")
            return 


        if ctx.author.id in self.games[lId]["players"]:
            await ctx.send("You've already joined the game!")
            return  

        if self.games[lId]["IN_PROGRESS"]:
            await ctx.send("There is already a game in progress in this channel. \
You can start another one in a different channel or wait for this one to finish.")
            return

        self.games[lId]["players"].append(ctx.author.id)
        await ctx.send("<@" + str(ctx.author.id) + "> has successfully joined!")

    @commands.command()
    async def fstart(self, ctx):
        lId = str(ctx.channel.id)

        if lId not in self.games:
            await ctx.send("There is no game to start. You can create one \
using `$five`.")
            return 

        if len(self.games[lId]["players"]) < 1:
            await ctx.send("There must be at least one player to play! You \
can join the game using `$fjoin`.")
            return 

        if self.games[lId]["IN_PROGRESS"]:
            await ctx.send("The game has already begun!")
            return

        self.games[lId]["IN_PROGRESS"] = True 

        self.init_player_cards(lId)
        await self.display_player_cards(lId, ctx)
        await self.begin_player_cards(lId, ctx)

    def init_player_cards(self, lId):
        game = self.games[lId]

        for i in range(game["CARD_POOL"]):
            game["cards"].extend([i+1] * game["CARD_REPEAT"])

        for player in game["players"]:
            game["numbers"][player] = [[0] * game["GRID_SIZE"] for i in range(game["GRID_SIZE"])]

    async def display_player_cards(self, lId, ctx):
        g = self.games[lId]
        gs = g["GRID_SIZE"]

        for player in g["players"]:
            emb = discord.Embed(title="Five - cards", color=discord.Color.blue())

            user = await self.bot.fetch_user(player)
            val = ""

            for i in range(gs):
                for j in range(gs):
                    val += "`" + str(g["numbers"][player][i][j]) + "` "
                val += "\n"

            emb.add_field(name=user.name, value=val.rstrip())
            emb.add_field(name="Current score:", value=self.calc_player_grid(g["numbers"][player], g["GRID_SIZE"]), inline=False)

            await ctx.send(embed=emb)
    
    async def begin_player_cards(self, lId, ctx):
        g = self.games[lId]

        if g["CURRENT_CARD_COUNT"] >= g["GRID_AREA"]:
            await self.fend(self, ctx)

        cn = random.randint(0, len(g["cards"])-1)
        card = g["cards"][cn]
        g["cards"].remove(card)

        await ctx.send("Your card is: **" + str(card) + "**")

        g["CURRENT_CARD"] = card 
        g["CURRENT_CARD_COUNT"] += 1
        g["CURRENT_WAITING"] = g["players"].copy()

    @commands.command()
    async def fplace(self, ctx, r, c):
        lId = str(ctx.channel.id)
        g = self.games[lId]

        r = int(r)
        c = int(c)

        if ctx.author.id not in g["players"]:
            await ctx.send("You aren't in the game.")
            return

        if r >= g["GRID_SIZE"] or c >= g["GRID_SIZE"] or r < 0 or c < 0:
            await ctx.send("Your input was out of range of the board. Remember, \
the labeling is 0-4 rows, 0-4 columns.")
            return

        # board
        b = g["numbers"][ctx.author.id]

        if b[r][c] != 0:
            await ctx.send("This spot is already taken!")
            return

        b[r][c] = g["CURRENT_CARD"]

        g["CURRENT_WAITING"].remove(ctx.author.id)

        await ctx.send("You successfully placed your card in r" + str(r) + "c" + str(c))
        await self.display_player_cards(lId, ctx)

        if len(g["CURRENT_WAITING"]) < 1:
            await self.begin_player_cards(lId, ctx)

    @commands.command()
    async def fskip(self, ctx):
        lId = str(ctx.channel.id)

        await ctx.send("Skipping...")
        await self.begin_player_cards(lId, ctx)

    @commands.command()
    async def fend(self, ctx):
        lId = str(ctx.channel.id)

        if lId not in self.games:
            await ctx.send("u dumb")
            return 

        if not self.games[lId]["IN_PROGRESS"]:
            await ctx.send("Asdflkj")
            return

        # cleanup
        await self.calc_player_scores(lId, ctx)
        self.games.pop(lId, None)

    async def calc_player_scores(self, lId, ctx):
        g = self.games[lId]

        scores = {}

        for player in g["players"]:
            scores[player] = self.calc_player_grid(g["numbers"][player], g["GRID_SIZE"])

        scores = dict(sorted(scores.items()))

        emb = discord.Embed(title="Five - final scores", color=discord.Color.purple())

        place = 1

        for i in scores:
            usr = await self.bot.fetch_user(i)
            emb.add_field(name="#" + str(place), value=usr.name + " - " + str(scores[i]) + " points")
            place += 1

        await ctx.send(embed=emb)

    def calc_player_grid(self, board, gs):
        score = 0
        for i in range(gs):
            # row
            r = [board[k][i] for k in range(gs)]
            score += self.calc_player_adj(r)

            # column
            c = board[i]
            score += self.calc_player_adj(c)
        return score

    def calc_player_adj(self, group):
        cur = -1 
        streak = 1 
        score = 0

        for i in group:
            if i != cur:
                score += streak * cur if streak > 1 else 0
                cur = i 
            else:
                streak += 1
        score += streak * cur if streak > 1 else 0

        return score

def setup(bot):
    bot.add_cog(Five(bot))
