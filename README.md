# sigmacat v1.3.0

This documentation serves as an in-depth record of all the components of the sigmacat bot. It's long and technical, so perhaps just using the **$help** command is enough information for you. If not, you can keep reading.

Contact me on discord if you have questions or want to contribute at
ricez cakes#8192

Join O Gang server https://discord.gg/wdFz7As9Er to get exclusive beta games, give suggestions and bug reports, and be notified about sigmacat updates.

### (Most recent update) 1.3.0: Blackjack!

- Play a game of blackjack with **$blackjack**!
- Added leaderboard for greed control
- Monetization for reaper only requires 5 active players
- Roulette minimum reverted to 1 instead of 5% of your net worth
- little more housekeeping

The full changelog can be found at the bottom of the documentation.

## Currency system
Currency is measured in O-bucks.

Commands:

 - **$balance** to check your balance
 - **$daily** to collect 1000 O-bucks once a day
 - **$give (ping user here) (amount to give)** to give another player O-bucks. Note that there is a 10% tax when doing so. You can give O-bucks to sigmacat itself, but you won't get it back again, unless...?
 - **$welfare** to get 1 O-buck if you're completely out.

## Reaper
A simple game about waiting and patience. You can "reap", in which you claim the points that have been building up since the last person reaped. The longer you wait, the more points you get, but be careful - other people may reap before you. First person to a set score wins.

To prevent overpowered timezone advantage getting huge night reaps, there is a tapering function implemented. In a nutshell, your points go up 1:1 with the number of seconds elapsed for smaller values of points, and approaches 1:5 for large reaps. (The specific function is 4800 \* arctan(points/6000)+ points/5.)

Occasionally, you can get a multiplier, doubling (or more!) the amount of points you would have gotten with the reap. Note that multipliers are applied *after* both tapering and O-buck distribution. The probabilities for multiplier is 1/4 to get 2x, and then 1/2 for each subsequent 0.5x after that. So 3.5x or higher would be 1/32, 4x or higher would be 1/64, 4.5x or higher would be 1/128, and so on.

For now, all reaper games are *monetized*, meaning that O-bucks are involved. Specifically:
 - Unlike games that are not monetized, there is no set wait period between consecutive reaps. The only thing stopping you from spam reaping is your wallet.
 - It costs 100 O-bucks to reap and that number increases by 5% every time you reap
 - You earn O-bucks for reaping using the formula (points-1500)/25
 - All spent O-bucks are placed in a prize pool to be distributed once someone wins
 - Distribution is as follows: k \* (prize pool) * (your score) / (sum of everyone's scores)
 - k is equal to 1.5 for top 3, 1.2 for #4 and #5, 1 for 6-10, and 0 for everyone else.
 - In addition, 1st place can receive *overkill* rewards, where they gain 1 O-buck for every 5 points they earn past the minimum score required to win.

### ADMIN ONLY COMMANDS
 - **$start_game (max_points)** begins a new reaper game. *Make sure you do this in a designated channel for reaper.* max_points is recommended to be between 50k and 200k for balance reasons and must be above 25k to qualify for O-buck rewards. Your reaper game is now tied to this channel, and keyword commands will only work in this channel.
 - **$end_game** ends the current reaper game. Note that even if your game qualifies for O-buck rewards, *ending the game before someone wins will not give any awards*. Therefore, make sure to use this command with extreme caution.

### Keyword commands
 - **reap** allows you to reap, claiming the points that have accumulated. 
 - **rank** shows you the current number of points that you have.
 - **timer** displays the current *time* since someone last reaped. It does not display the points that you would get from such a reap, or whether you would get a multiplier on the reap.
 - **leaderboard** displays the top 10 scores for the current game, using nicknames. If a player is no longer in the server, it shows "[user not found]". It also displays the score required to win. 
 - **nextreap** displays the time required until you can reap again, if the game is not monetized.
 - **cost** displays the current reap cost (how much you have to pay to reap). 
 - **pool** displays the *sum of all O-bucks spent by purely reaping*. It does *not* show the total amount of O-bucks to be distributed at the end of the game, that number is related but different. See the distribution calculation methods for more info on this.

## Greed Control
A simple game about, as the name implies, controlling the natural human instinct to obtain as much of a resource as possible. 
 - Each day, you can select a number from 1 to a certian limit (for now 1 to 5).
 - Each day at midnight, points are distributed equal to the number you chose *divided by* the total number of people who *also* chose your number.
 - First to a set number of points wins. (Points are rounded to 4 decimal places.)

Note that Greed Control has not been integrated with the currency system yet.

Commands:

 - **$greed** lets you pick a number for the day. *Keep your number secret*. After you use the command, the bot will DM you and you have fifteen seconds to respond with a number. If you use this command multiple times in a day, you will merely update your pick instead of picking multiple times. 
 - **$greederboard** displays the global greed leaderboard, including the top 10 usernames and scores.

## Roulette
Spin the roulette wheel! Note that unlike actual roulette, you can only bet on one thing per spin, and you cannot play a game with multiple people for now. The wheel will spin automatically after you bet. The numbers on the wheel include 1-36, 0, and 00. 

There are a variety of bets available:

Bets that pay more than you bet:
 - **single**: self explantory. Bet on the wheel spinning the exact number you picked. If you win, you earn 35x your bet. Specifiers: the number you are betting on
 - **double**: Bet on the wheel spinning one of two adjacent numbers on the roulette table. If you win, you earn 17x your bet. Specifiers: the two numbers you are betting on
 - **street**: Bet on the wheel spinning one of three numbers in a column. If you win, you earn 11x your bet. Specifiers: the bottom number of the column
 - **corner**: Bet on the wheel spinning one of four numbers in a square. If you win, you earn 8x your bet. Specifiers: the bottom left number of the square
 - **green**: Bet on the wheel spinning either 0 or 00. If you win, you earn 17x your bet. Specifiers: none
 - **basket**: Bet on the wheel spinning one of 0, 00, 1, 2, or 3. If you win, you earn 6x your bet. Specifiers: none
 - **row**: Bet on the wheel spinning one of twelve numbers in a row. If you win, you earn 2x your bet. Specifiers: the row number
 - **dozen**: Bet on the wheel spinning one of twelve numbers in a block. If you win, you earn 2x your bet. Specifiers: the group number

Bets that pay out exactly how much you bet (no specifiers):
 - **low** or **high**: Bet on the wheel spinning either between 01 and 18 or between 19 and 36, respectively.
 - **even** or **odd**: Bet on the result being either even or odd, respectively.
 - **red** or **black**: Bet on the wheel spinning a red number or a black number, respectively.

Red numbers include: 32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14, 9, 18, 7, 12, 3

Black numbers include: 15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20, 31, 22, 29, 28, 35, 26

Commands:

 - **$rbet (bet amount) (bet type) (specifiers if required)** lets you spin the roulette wheel. If you try to bet a negative number, something interesting happens...
 - **$rtable** displays the roulette table.
 - **$rhelp** shows the types of bets without having to come back here all the time.

## Five by Five
Singleplayer or multiplayer card game. 25 cards are drawn from a total of 40, one at a time. Face cards are removed, and aces are worth 1. Each time a card is drawn, each player picks a place on a 5x5 grid to place it. Once all cards have been placed, score is calculated as follows:
 - Each row *and* each column is calculated seperately, then summed up.
 - Whenever there are two or more numbers of the same value next to each other in the same row or column, they get points. For example, [7, 9, 9, 9, 5] gives 27 points and [6, 4, 4, 9, 1] gives 8 points, but [5, 6, 1, 3, 1] gives no points.

Commands:
 - **$five** activates and begins *recruiting* for a game. This means that until the game has been started, anyone can join the room and play the game once it starts. You can't play multiple games of five-by-five in the same channel, so kindly wait for the current game to finish if it is still active.
 - **$fjoin** allows you to join a game that has been activated but not started.
 - **$fstart** begins the game, as long as there is at least one player in the waiting room.
 - **$fplace (row number) (column number)** places your current card into the position that you want it to be, as long as it is vacant (denoted with a 0). Note that the row and column labeling systems are **zero-indexed** (i.e. they go from 0-4 instead of 1-5), left to right and top to bottom.
 - **$fskip** skips any players who haven't placed their cards if they are taking too long.
 - **$fend** ends the current game in that channel. Note that you dont have to be in the game to end it - in case the previous players have just left it there. However, be courteous and don't end a game that is obviously in progress.

## Blackjack

Minimalistic single-player blackjack game. Two cards are dealt to the player and to the dealer, and one of the dealer's card is covered up (denoted with an "X"). Face cards are worth 10, aces are worth either 1 or 11, and all other cards their numerical values. 

If the player's cards automatically sum to 21, they have a "natural" and earn 1.5x their bet. If the dealer's cards sum to 21, the player automatically loses. If both do, it's a standoff and no one gets anything.

During the player's turn, the player can repeatedly "hit" (get a new card) and then decide to "stand" (end their turn). They have 15 seconds to make this choice. If at any point their sum goes above 22 (both sums if an ace is in their hand), they "bust" and automatically lose.

Then, the dealer's turn begins. The dealer must hit until they have at least a sum of 17, at which point they must stand. Similarly, if a dealer busts, the player automatically wins.

If no one has busted, the player with the higher sum wins. If they have equal sums, it is a standoff and the player doesn't earn or lose any money.

Note that card counting will never work because cards are chosen truly randomly, instead of a card pool to draw from.

Commands:

- **$blackjack (bet_amount)** begins a round of Blackjack.

## Changelog

For more details on any of the games mentioned, check their individual sections in this document.

### 1.2: Greed Control

 - Play a global game of greed control
 - Join O Gang discord server to see the distribution statistics for numbers selected, and to follow the announcements channel there to get those statistics in your own server
 - Play from any server that has sigmacat with **$greed**.

### 1.1: Roulette

 - Bet in a variety of ways with **$rbet**. The roulette wheel will automatically spin by using the command.
 - Reaper games can now be played in any server you like.

### 1.0: REAPER IS NOW UP!

 - Limited to O Gang discord server for now
 - Integrated with currency system
 - Reap with **reap** in the reaper channel

