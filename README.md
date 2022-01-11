# sigmacat v1.2.2

This documentation serves as an in-depth record of all the components of the sigmacat bot. It's long and technical, so perhaps just using the **$help** command is enough information for you. If not, you can keep reading.

Contact me on discord if you have questions or want to contribute at
ricez cakes#8192

# Changelog
For more details on any of the games mentioned, check their individual sections further in this document.
### Upcoming (1.3): Blackjack
### Most recent (1.2): Greed Control
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

# Features:
## Currency system
Currency is measured in O-bucks.
 - **$balance** to check your balance
 - **$daily** to collect 1000 O-bucks once a day
 - **$give** to give another player O-bucks. Note that there is a 10% tax when doing so.
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
 - Distribution is as follows:

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
 - 
