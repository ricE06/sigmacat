import discord
from discord.ext import commands, tasks
import random

class Five(commands.Cog):
    
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="five")
    async def play_five(self, ctx:commands.Context):
        # This is a program to play the classic card game Five by Five (multiplayer).
        # Twenty-five cards will be drawn from 40 cards (face cards removed). Aces are
        # worth one and all others are worth their numerical values. After each card is
        # drawn, the player must choose an empty location on their five by five grid to
        # place the card. Once all 25 cards have been placed, points will be calculated
        # for each row and each column as the sum of all sets of 2 or more adjacent numbers.
        # For example, [4, 4, 5, 7, 1] gives 8 points and [7, 9, 9, 9, 2] gives 27 points.
        # Rows or columns without any adjacent lines give no points.  
        # The goal is to get the largest point value. 

        # The labeling for the grid is 0-4 rows, 0-4 columns.
        # The size of the grid and the number of possible cards are adjustable.

        # Size of the grid (adjustable, default 5)
        GRID_SIZE = 5
        GRID_AREA = GRID_SIZE*GRID_SIZE
        # Number of possible cards (adjustable, default 10-4)
        CARD_POOL = 10
        CARD_REPEAT = 4

        # numbers is the list of the 25 numbers in the grid for each player,
        # arranged from left to right and subsequently top to bottom:
        # 0 1 2 3 4
        # 5 6 7 8 9
        # ...
        # cards is the list of all possible cards to draw from, will be 
        # Both lists will be filled in by init()
        numbers = {}
        cards = []

        message = ctx.message
        
        # Lets all players join
        async def pregame():
            # Size of the grid (adjustable, default 5)
            global GRID_SIZE
            GRID_SIZE = 5
            global GRID_AREA
            GRID_AREA = GRID_SIZE*GRID_SIZE
            # Number of possible cards (adjustable, default 10-4)
            global CARD_POOL
            CARD_POOL = 10
            global CARD_REPEAT
            CARD_REPEAT = 4
            await message.channel.send("Game starting. To join, type `join`. To\
 start the game, type `start`. To play a quick game, type `small`.")
            # List of player IDs that wish to play
            players = []
            # Checks if a player wishes to join
            def check_join(msg):
                if str(msg.content) == "join" and msg.author.id not in players:
                    return True
                    print("Yay")
                else:
                    return False
            # Checks if a player wishes to start the game
            def check_end(msg):
                if str(msg.content) == "start" and len(players)>0:
                    return True
                else:
                    return False
            def check_edit(msg):
                if str(msg.content) == "small":
                    return True
                else:
                    return False
            def check(msg):
                return check_join(msg) or check_end(msg) or check_edit(msg)
            # Adds each new player to the list and checks to end the pregame
            while True:
                msg = await self.client.wait_for("message", check=check)
                if check_join(msg) == True:
                    await message.channel.send("Joined!")
                    players.append(msg.author.id)
                if check_end(msg) == True:
                    await message.channel.send("Game starting.")
                    break
                if check_edit(msg) == True:
                    await message.channel.send("Small mode on.")
                    GRID_SIZE = 3
                    print(GRID_SIZE)
                    GRID_AREA = GRID_SIZE*GRID_SIZE
                    CARD_POOL = 5
            print(GRID_SIZE)
            return players
                
        # Gets the card corresponding to the index in the list of possible
        # cards and sets it to the maximum number of characters needed
        def get_card(player, index):
            card = int(numbers[player][index])
            emoji_list = [":one:",":two:",":three:",":four:",":five:",":six:",":seven:",":eight:",":nine:",":keycap_ten:",":blue_square:"]
            return emoji_list[card-1]

        # Displays the grid for each player (takes in player ID)
        async def display(players):
            for player in players:
                user = await self.client.fetch_user(player)
                string = user.name + "'s board \n" + "Current score: " + str(calc_grid(numbers[player], message.channel)) + "\n"
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        string = string + get_card(player, GRID_SIZE*i+j)
                    if i < (GRID_SIZE - 1):
                        string = string + "\n"
                await message.channel.send(string)

        # Fills in the possible cards in the cards list, adding four of
        # each number from 1 to the max
        async def init(players):
            for i in range(CARD_POOL):
                for j in range(CARD_REPEAT):
                    cards.append(i+1)
            for player in players:
                player_numbers = []
                for i in range(GRID_AREA):
                    player_numbers.append(0)
                numbers[player] = player_numbers
            print(numbers)
            

        # Gives the player a random card from the cards list, removes the
        # card from the list
        async def give_card(channel):
            card_num = random.randint(0, len(cards)-1)
            print(len(cards))
            card = str(cards[card_num])
            await channel.send("Your card is: " + card)
            cards.remove(cards[card_num])
            return card

        # Calculates the score for ONE row or column of numbers
        def check_adj(group):
            streak = 1
            score = 0
            for i in range(len(group)-1):
                if group[i+1] == group[i]:
                    streak += 1
                else:
                    if streak >= 2:
                        score += streak*int(group[i])
                    streak = 1
            if streak >= 2:
                score += streak*int(group[len(group)-1])
            return score

        # Calculates the score for the ENTIRE grid
        def calc_grid(player_numbers, channel):
            score = 0
            for i in range(GRID_SIZE):
                # rows
                list = []
                for j in range(GRID_SIZE):
                    list.append(player_numbers[GRID_SIZE*i+j])
                score += check_adj(list)
                # columns
                list = []
                for j in range(GRID_SIZE):
                    list.append(player_numbers[i+GRID_SIZE*j])    
                score += check_adj(list)
            return score

        # Calculates the scores for each player and displays them (automatic
        # ordering system in development)
        async def calc_scores(players):
            string = "**Final scores:** "
            scores = {}
            for player in players:
                scores[player] = calc_grid(numbers[player], message.channel)
            # Sorts the scores
            scores = sorted(scores.items())
            scores = dict(scores)
            for player in scores:
                user = await self.client.fetch_user(player)
                string = string + "\n" + user.name + ": " + str(scores[player])
            await message.channel.send(string)

        # Gives the player a card, asks for the position to place it, and
        # displays the grid with the new card until the grid is filled
        async def main_loop(players):
            channel = message.channel
            card_count = 0
            while True:
                # Checks if the grid is filled
                if card_count >= GRID_AREA:
                    break
                # Gives a card
                card = await give_card(channel)
                card_count += 1
            
                # Generates a list of which players still need to pick valid position
                waiting = []
                for player in players:
                    waiting.append(player)
                # Generates a dictionary of the position for each player
                positions = {}
                for player in players:
                    positions[player] = [0, 0]
                # Gets a position and asks until all players give a valid position
                while len(waiting) != 0:
                    # Generates a list of which players still need to pick x and y positions
                    waitingx = []
                    waitingy = []
                    for player in waiting:
                        waitingx.append(player)
                        waitingy.append(player)
                    # Checks if x and y pos are in range
                    def check(m):
                        try:
                            message = int(m.content)
                        except ValueError:
                            return False
                        return m.author.id in waiting
                    # Asks for x and y positions
                    await channel.send("What column do you want this card in?")
                    while len(waitingx) > 0:
                        msg = await self.client.wait_for("message", check=check)
                        xpos = int(msg.content)
                        positions[msg.author.id][0] = xpos
                        if xpos >= -1 and xpos < GRID_SIZE:
                            waitingx.remove(msg.author.id)
                            if xpos == -1:
                                await channel.send("Game ended.")
                                return 3
                        elif xpos < -1 or xpos >= GRID_SIZE:
                            await channel.send("Out of range!")
                    await channel.send("What row do you want this card in?")
                    while len(waitingy) > 0:
                        msg = await self.client.wait_for("message", check=check)
                        ypos = int(msg.content)
                        positions[msg.author.id][1] = ypos
                        if ypos >= -1 and ypos < GRID_SIZE:
                            waitingy.remove(msg.author.id)
                            if ypos == -1:
                                await channel.send("Game ended.")
                                return 3
                        elif ypos < -1 or ypos >= GRID_SIZE:
                            await channel.send("Out of range!")
                    # Adds the card to the grid, checks if vacant
                    num_waiting = len(waiting)
                    passed = []
                    for i in range(num_waiting):
                        player = waiting[i]
                        user = await self.client.fetch_user(player)
                        if numbers[player][GRID_SIZE*positions[player][1]\
                        +positions[player][0]] == 0:
                            numbers[player][GRID_SIZE*positions[player][1]\
                            +positions[player][0]] = card
                            passed.append(player)
                        else:
                            await channel.send("**" + user.name + "**, that spot is already taken!")
                    for player in passed:
                        waiting.remove(player)
                await display(players)

        # Main program (sets up board, displays board, plays the main game,
        # and calculates and displays the scores)
        async def main():
            players = await pregame()
            await init(players)
            await display(players)
            await main_loop(players)
            await calc_scores(players)

        await main()

def setup(client):
    client.add_cog(Five(client))
