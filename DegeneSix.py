# Work with Python 3.6
import numpy as np
import os
import discord
from discord.ext.commands import Bot, when_mentioned_or
import sqlite3

#from degenesis_messages import *

#joke:
import time

# Setup database
try:
	connection = sqlite3.connect('degenesis.db')
	cursor = connection.cursor()
	with open('degenesis-schema.sql') as file:
		cursor.executescript(file.read())
except Exception as e:
	print(e)
	print("Database error")
	exit()

# Setup Bot
BOT_PREFIX = ("!")
TOKEN = os.environ.get('TOKEN')
bot = Bot(command_prefix=when_mentioned_or(*BOT_PREFIX))
print("Current token: " + TOKEN)


def roll(numDice):
	autos = max(numDice-12, 0)
	rolls = np.random.randint(1, 7, numDice-autos)
	ones = countOnes(rolls)
	successes = countSuccesses(rolls)
	triggers = countTriggers(rolls)
	return {
		"rolls": rolls,
		"ones": ones,
		"successes": successes,
		"triggers": triggers
	}

def countOnes(rolls):
	return (rolls == 1).sum()

def countSuccesses(rolls):
	return (rolls > 3).sum()

def countTriggers(rolls):
	return (roll == 6).sum()

# Roller
@bot.command(
    name='Degene6',
    description="Rolls a Degenesis dice pool.",
    brief="Sacrifice everything",
    aliases=['D6', '6pool','roll','dee6'],
    pass_context=True)
async def degenesix(context,actionNumber:int,difficulty=0):
    autos = 0 if actionNumber < 13 else actionNumber-12
    actionNumber = 12 if actionNumber > 13 else actionNumber
    roll = np.random.choice([1,2,3,4,5,6],actionNumber)
    successes = (roll > 3).sum()
    successes += autos
    triggers = (roll == 6).sum()
    ones = (roll == 1).sum()
    degEmoji = get(context.message.guild.emojis, name="degenesis")

    if difficulty:
        result = (f'*Success!* {degEmoji}\n' if successes >= difficulty else "Failure!\n") if ones <= successes else '*It\'s a botch!* :skull:\n'
        msg = "%s needs %d successes and rolls:" % (context.author.mention,difficulty) if autos == 0 else "%s needs %d successes, already has %d automatic and rolls:" % (context.author.mention,difficulty,autos)
    else:
        result = '' if ones <= successes else '*It\'s a botch!* :skull:\n'
        msg = "%s rolls:" % (context.author.mention) if autos == 0 else "%s has %d automatic successes and rolls:" % (context.author.mention, autos)
    msg+= " \n %s \n %d successes, %d triggers \n %s" % (', '.join(map(str,roll)),
    successes,
    triggers,
    result)
    await context.send(msg)

# Initiative stuff
@bot.command(
	name='start-initiative',
	brief='Allow calls for initiative in this channel',
	pass_context=True)
async def initiativeStart(context, label:str=None):
	global cursor
	try:
		async with context.typing():
			#TODO - check and send if we deleted an initiative
			id = context.channel.id
			cursor.execute("REPLACE INTO initiatives(channel_id, label) VALUES(?,?)", (id, label))
			cursor.execute("DELETE FROM characters WHERE channel_id=?", (id,))
			msg = "Initiative " + (label + " " if label else "") + "started!\nUse `!initiative [name] [dice] [ego]` (name and ego are optional)"
		await context.send(msg)
	except Exception as e:
		await context.send("Failed to start initiative. Try a different channel, or email daviegourevitch@gmail.com for immediate help")
		await context.send(e)

@bot.command(
	name='initiative',
	brief='Add yourself to the initiative',
	pass_context=True)
async def initiativeAdd(context, *args):
	global cursor
	try:
		async with context.typing():
			inputs = parseInitiativeAdd(args)
			name = inputs[0]
			dice = inputs[1]
			ego = inputs[2]
			msg = "name " + name if name else "" + " dice " + dice if dice else "" + " ego " + ego if ego else ""
			await context.send(msg)
			# Check that the initiative exists and is open
			cursor.execute("SELECT label, is_closed FROM initiatives WHERE channel_id=?", (context.channel.id,))
			initiative = cursor.fetchone()
			if (not initiative):
				return context.send("There is no active initiative in this channel.")
			if (initiative[1] != 0):
				return context.send("The active initiative in this channel is not accepting players.")
			# Check if the player is already in that initiative
			cursor.execute("SELECT discord_id, name FROM characters WHERE channel_id=?", (context.author.id,))
			characters = cursor.fetchall()
			if (checkDuplicate(characters, name)):
				msg = "" + name if name else context.author.display_name + " was already in the initiative. Overwriting..."
				await context.send(msg)
			# Add them and send message
			cursor.execute("REPLACE INTO characters(channel_id, discord_id, name, num_dice, num_ego) VALUES(?,?,?,?,?)", (context.channel.id, context.author.id, name, dice, ego))
			msg = "" + name if name else context.author.mention + " was successfully added to the initiative"
		await context.send(msg)
	except Exception as e:
			await context.send("An error occurred while adding you to the initiative")
			await context.send(e)

def parseInitiativeAdd(args):
	if len(args) == 0:
		raise BadArgument() #todo
	if len(args) == 1:
		tuple = (None, args[0], None)
	if len(args) >= 3:
		tuple = (args[0], args[1], args[2])
	if (type(args[0]) is str):
		tuple = (args[0], args[1], None)
	else:
		tuple = (None, args[0], args[1])
	return tuple

def checkDuplicate(characters, name):
	if (len(characters) == 0 and not name):
		return False
	for character in characters:
		if character[1] == name:
			return True
	return False


@bot.command(
	name='context',
	brief='Add yourself to the initiative',
	pass_context=True)
async def initiativeNext(context, *args):
	global cursor
	try:
		print(p)
	except Exception as e:
			await context.send("An error occurred while moving to next initiative")
			await context.send(e)


@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name)




bot.run(TOKEN)
