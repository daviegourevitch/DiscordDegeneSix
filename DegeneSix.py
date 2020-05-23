# Work with Python 3.6
import numpy as np
import os
import discord
from discord.ext.commands import Bot, when_mentioned_or
import sqlite3

# setup database
try:
	connection = sqlite3.connect('degenesis.db')
	c = connection.cursor()
	with open('degenesis-schema.sql') as file:
		c.executescript(file.read())
except Exception as e:
	print(e)
	print("Database loading problem")
	exit()

BOT_PREFIX = ("!")
TOKEN = os.environ.get('TOKEN')
print("Current token: " + TOKEN)

bot = Bot(command_prefix=when_mentioned_or(*BOT_PREFIX))

bot.haveUsedInitiative = False

@bot.command(
    name='Degenesis Dice Roller',
    brief="Roll a dice pool for Degenesis",
    aliases=['DD', 'roll','deg6'],
    pass_context=True)
async def degenesix(context,actionNumber:int,difficulty=0):
    autos = max(actionNumber-12, 0)
    actionNumber -= autos

    roll = np.random.randint(1, 7, actionNumber)
    successes = (roll > 3).sum()
    successes += autos
    triggers = (roll == 6).sum()
    ones = (roll == 1).sum()

    if difficulty:
        result = ('*Success!* <:degenesis:710968855098294272>\n' if successes >= difficulty else "Failure!\n") if ones <= successes else '*It\'s a botch!* :skull:\n'
        msg = "%s needs %d successes and rolls:" % (context.author.mention,difficulty) if autos == 0 else "%s needs %d successes, already has %d automatic and rolls:" % (context.author.mention,difficulty,autos)
    else:
        result = '' if ones <= successes else '*It\'s a botch!* :skull:\n'
        msg = "%s rolls:" % (context.author.mention) if autos == 0 else "%s has %d automatic successes and rolls:" % (context.author.mention, autos)
    msg+= " \n %s \n %d successes, %d triggers \n %s" % (', '.join(map(str,roll)),
    successes,
    triggers,
    result)
    await context.send(msg)

@bot.command(
	name='Start initiative',
	brief='Allow calls for initiative',
	aliases=['start-initiative'],
	pass_context=True)
async def initiativeStart(context, initiativeName=None):
	global c
	try:
		c.execute("SELECT * FROM initatives")
		asdf = c.fetchone()
		await context.send("fetched data is")
		await context.send(asdf)
	except Exception as e:
		print(e)
	if (initiativeName):
		await context.send("Initiative was already active.")
	else:
		await context.send("Starting initiative. Use !initiative [name] [dice]")

	bot.initiativeActive = True
	bot.maxPlayers = numPlayers

@bot.command(
	name='Register for initiative',
	brief='Add yourself to the initiative',
	aliases=['initiative'],
	pass_context=True)
async def initiativeStart(context, playerName, numDice):
	if (not bot.initiativeActive):
		await context.send("Please start an initiative first")
	else:
		# roll dice
		# track successes and triggers
		# add to the initiative array
		await context.send("Not implemented yet")


@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name)



bot.run(TOKEN)
