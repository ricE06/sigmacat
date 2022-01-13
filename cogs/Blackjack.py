import discord
from discord.ext import commands
import random
import asyncio

class Blackjack(commands.Cog, description="Classic game of blackjack."):
	'''
	The goal is to get the largest hand possible without going above a sum of 21 (or "busting"). Number cards are worth their numerical values and face cards are worth 10, with the exception of the ace, which can be worth either 1 or 11. 
	Once the game begins, two cards are dealt to you face-up. Two are also dealt to the dealer, one of which is facedown. Each round, you can either "hit", or get a new card, or "stand", and end your turn. Then, the dealer hits until they have 17 or above. The winner is whoever has a higher total without busting. 
	'''

	def __init__(self, client: commands.Bot):
		self.client = client
		self.Currency = self.client.get_cog("Currency")

	# Gives a card to the hand (either player of dealer)
	# Aces are denoted by 1
	def give_card(self, hand):
		card = random.randint(1, 13)
		hand.append(card)

	# Calculates the sum of numbers in a hand, accounting for aces (note that there is no need for any more than two possible numbers since max sum is 21)
	def calc_sum(self, hand, hidden_second_card):
		if hidden_second_card == True:
			return (0,)
		total = 0
		for i in hand:
			if i >= 10:
				value = 10
			else:
				value = i
			total += value
		if 1 in hand and (total+10) <= 21:
			return (total, total+10)
		else:
			return (total,)

	# Converts the list of numbers into list of cards
	def convert(self, hand, hidden_second_card):
		display = []
		for i in range(len(hand)):
			if i == 1 and hidden_second_card == True:
				card = "X"
			else:
				if hand[i] == 1:
					card = "A"
				elif hand[i] == 11:
					card = "J"
				elif hand[i] == 12:
					card = "Q"
				elif hand[i] == 13:
					card = "K"
				else:
					card = str(hand[i])
			display.append(card)
		return (", ").join(display)

	# Sends the message to be displayed
	async def display(self, channel, player, dealer, hidden_second_card):
		string = "Dealer's cards: " + self.convert(dealer, hidden_second_card) + "\n" + "Your cards: " + self.convert(player, False) + "\n" + "Your sum: "
		player_sum = self.calc_sum(player, False)
		if len(player_sum) == 1:
			string += str(player_sum[0])
		else:
			string += str(player_sum)
		string += "\n" + "Dealer's sum: "
		dealer_sum = self.calc_sum(dealer, hidden_second_card)
		if len(dealer_sum) == 1:
			string += str(dealer_sum[0])
		else:
			string += str(dealer_sum)
		await channel.send(string)		


	# Actual game
	@commands.command(name="blackjack", help="Play blackjack! Syntax: `$blackjack (bet amount)`")
	async def blackjack(self, ctx, amount):
		channel = ctx.message.channel
		user_id = ctx.message.author.id
		prev_amount = int(self.Currency.get_current(user_id))
		

		# Makes sure bet is valid
		if int(amount) > prev_amount:
			await channel.send("You can't bet more than you own!")
			return
		if int(amount) == 0:
			await channel.send("You must bet *something*.")
			return
		elif int(amount) < 0:
			amount = prev_amount
			await channel.send("Successfully going all in!")

		# Initializes, gives dealer and player their hands
		player = []
		dealer = []
		self.give_card(player)
		self.give_card(player)
		self.give_card(dealer)
		self.give_card(dealer)
		# Checks for immediate naturals
		if 21 in self.calc_sum(player, False):
			player_natural = True
		else:
			player_natural = False
		if 21 in self.calc_sum(dealer, False):
			dealer_natural = True
		else:
			dealer_natural = False

		await self.display(channel, player, dealer, not dealer_natural)

		# Checks for naturals
		if player_natural == True and dealer_natural == False:
			await channel.send("You got a blackjack and 1.5x your bet!")
			self.Currency.change(user_id, round(1.5*int(amount)))
			return
		elif player_natural == False and dealer_natural == True:
			await channel.send("The dealer got a blackjack! You lost.")
			self.Currency.change(user_id, -int(amount))
			return
		elif player_natural == True and dealer_natural == Ture:
			await channel.send("Standoff! Both you and the dealer have natural blackjacks.")
			return

		# Player's turn
		while True:
			if self.calc_sum(player, False)[0] > 21:
				await channel.send("You busted!")
				self.Currency.change(user_id, -int(amount))
				return

			def check(msg):
				if msg.content != "hit" and msg.content != "stand":
					return False
				return msg.channel == channel and msg.author == ctx.message.author

			await channel.send("Would you like to hit or stand?")
			try:
				msg = await self.client.wait_for("message", check=check, timeout=15)
			except asyncio.TimeoutError:
				await channel.send("You timed out and lost your bet!")
				self.Currency.change(user_id, -int(amount))
				return
			if msg.content == "stand":
				await channel.send("Ended your turn.")
				break
			elif msg.content == "hit":
				self.give_card(player)
				await self.display(channel, player, dealer, True)
			else:
				await channel.send("tf")
				return

		await self.display(channel, player, dealer, False)
		# Dealer's turn
		while True:
			await asyncio.sleep(1)
			if self.calc_sum(dealer, False)[0] > 21:
				await channel.send("The dealer busted! You earned " + str(amount) + " O-bucks.")
				self.Currency.change(user_id, int(amount))
				return
			elif self.calc_sum(dealer, False)[-1] >= 17:
				await channel.send("The dealer stands.")
				break
			else:
				self.give_card(dealer)
				await self.display(channel, player, dealer, False)

		# Determine who wins
		dealer_sum = self.calc_sum(dealer, False)[-1]
		player_sum = self.calc_sum(player, False)[-1]
		if player_sum > dealer_sum:
			await channel.send("You won! You earned " + str(amount) + " O-bucks.")
			self.Currency.change(user_id, int(amount))
			return
		elif player_sum == dealer_sum:
			await channel.send("Standoff! No one gets anything.")
			return
		elif player_sum < dealer_sum:
			await channel.send("You lost!")
			self.Currency.change(user_id, -int(amount))
			return

def setup(client):
	client.add_cog(Blackjack(client))
	# global Currency
	# Currency = client.get_cog("Currency")