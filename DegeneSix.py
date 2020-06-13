# Work with Python 3.6
import numpy as np
import os
import discord
from discord.ext.commands import Bot, when_mentioned_or
import sqlite3


TOKEN = "NzA5NjA5MjA5NDEwNDg2Mjg0.XuPG7g.1Wpeb7bjTx74CzphFHepa0GSR4E"

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
#TOKEN = os.environ.get('TOKEN')
bot = Bot(command_prefix=when_mentioned_or(*BOT_PREFIX))
print("Current token: " + TOKEN)


def roll(numDice, numEgo):
	totalDice = (numDice + numEgo if numEgo else numDice)
	autos = max(totalDice-12, 0)
	results = np.random.randint(1, 7, totalDice-autos)
	ones = countOnes(results)
	successes = countSuccesses(results)
	triggers = countTriggers(results)
	return {
		"results": results,
		"ones": ones,
		"successes": successes,
		"triggers": triggers
	}

def countOnes(rolls):
	print(rolls)
	return (rolls == 1).sum()

def countSuccesses(rolls):
	print(rolls)
	return (rolls >= 4).sum()

def countTriggers(rolls):
	print(rolls)
	return (rolls == 6).sum()

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

    if difficulty:
        result = ('*Success!* <:degenesis:721181871345631253>\n' if successes >= difficulty else "Failure!\n") if ones <= successes else '*It\'s a botch!* :skull:\n'
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
	global cursor, connection
	msg = ""
	try:
		async with context.typing():
			cursor.execute("SELECT label FROM initiatives WHERE channel_id=?", (context.channel.id,))
			previousInitiative = cursor.fetchone()
			if (previousInitiative and len(previousInitiative) > 0):
				msg += "Deleting previous " + (("initiative \"" + str(previousInitiative[0]) +"\"") if previousInitiative[0] else "initiative") + "...\n"
			cursor.execute("REPLACE INTO initiatives(channel_id, label) VALUES(?,?)", (context.channel.id, label))
			cursor.execute("DELETE FROM characters WHERE channel_id=?", (context.channel.id,))
			cursor.execute("DELETE FROM initiative_values WHERE channel_id=?", (context.channel.id,))
			connection.commit()
			msg += "Initiative " + (label + " " if label else "") + "started!\nUse `!initiative [name] [dice] [ego]` (name and ego are optional) to join\nType `!next` to start!"
		await context.send(msg)
	except Exception as e:
		await context.send("Failed to start initiative. Try a different channel, or email daviegourevitch@gmail.com for immediate help")
		await context.send(e)

@bot.command(
	name='initiative',
	brief='Add yourself to the initiative',
	description='Use `!initiative [name] [dice] [ego]` to add yourself to this channel\'s initiative (name and ego are optional)',
	pass_context=True)
async def initiativeAdd(context, *args):
	global cursor, connection
	msg = ""
	try:
		await context.trigger_typing()
		parsedArgs = parseInitiativeAdd(args)
		if (not parsedArgs):
			await context.send("Invalid input. Use `!help initiative` for more info.")
			return
		name = parsedArgs[0]
		dice = parsedArgs[1]
		ego = parsedArgs[2]

		# Check that the initiative exists and is open
		cursor.execute("SELECT label, cur_initiative FROM initiatives WHERE channel_id=?", (context.channel.id,))
		initiative = cursor.fetchone()
		if (not initiative):
			await context.send("There is no active initiative in this channel.")
			return
		if (initiative[1] >= 0):
			msg += "The initiative in this channel has already started. You will join at the beginning of the next round\n"

		# Check if the player is already in that initiative
		cursor.execute("SELECT name FROM characters WHERE channel_id=? AND mention=?", (context.channel.id, context.author.mention))
		characters = cursor.fetchall()
		if (checkDuplicate(characters, name)):
			msg += ("" + name if name else context.author.display_name) + " was already in the initiative. Overwriting...\n"
		# Add them and send message
		cursor.execute("REPLACE INTO characters(channel_id, mention, name, num_dice, num_ego) VALUES(?,?,?,?,?)", (context.channel.id, context.author.mention, name, dice, ego))
		connection.commit()
		msg += "Player " + (name if name else context.author.mention) + " was added to the initiative with " + str(dice) + " dice" + ((" and " + str(ego) + " ego") if ego else "")
		await context.send(msg)
	except Exception as e:
			await context.send("An error occurred while adding you to the initiative")
			await context.send(e)

def parseInitiativeAdd(args):
	try:
		if (len(args) == 1 and type(int(args[0])) is int):
			return [None, int(args[0]), None]
		if (len(args) == 2):
			try:
				dice = int(args[0])
				ego = int(args[1])
				return [None, dice, ego]
			except:
				dice = int(args[1])
				return [args[0], dice, None]
		if (len(args) >= 3):
			dice = int(args[1])
			ego = int(args[2])
			return [args[0], dice, ego]
		return None
	except:
		return None

def checkDuplicate(characters, name):
	if (len(characters) == 0):
		return False
	if (len(characters) > 0 and len(name) == 0):
		return True
	for character in characters:
		if character[0] == name:
			return True
	return False

@bot.command(
	name='verbose',
	brief='Change the verbosity of the initiative functions',
	pass_context=True)
async def initiativeNext(context, option:str):
	global cursor, connection
	try:
		await context.trigger_typing()
		if (option.lower() == "on"):
			choice = False
		elif(option.lower() == "off"):
			choice = True
		else:
			await context.send("Please use `on` or `off`")
			return
		cursor.execute("REPLACE INTO initiatives(channel_id, verbose) VALUES(?,?)", (context.channel.id, int(choice)))
		connection.commit()
		msg = "Verbose level set to: `" + option + "`"
		await context.send(msg)
	except Exception as e:
		await context.send("Error while changing verbosity")
		await context.send(e)



@bot.command(
	name='next',
	brief='Move to the next round of initiative',
	aliases=['next-initiative'],
	pass_context=True)
async def initiativeNext(context, *args):
	global cursor, connection
	msg = ""
	try:
		await context.trigger_typing()

		# Grab the initiative
		cursor.execute("SELECT label, round_number, cur_initiative FROM initiatives WHERE channel_id=?", (context.channel.id,))
		initiative = cursor.fetchone()
		await context.send(str(initiative) + "asdf")
		if (not initiative or len(initiative) == 0):
			await context.send("There is no active initiative in this channel")
			return
		cur_initiative = initiative[2]

		# Grab the characters
		cursor.execute("SELECT mention, name, num_dice, num_ego from characters WHERE channel_id=?", (context.channel.id,))
		characters = cursor.fetchall()
		if (not characters):
			await context.send("There is no one in this channel's initiative")
			return

		# Check if we need to restart initiative
		if (cur_initiative < 0):
			msg += "Starting round " + str(initiative[1]) + " of initiative" + ((" " + initiative[0]) if initiative [0] else "") + "..."
			msg += str(initiative[1])
			#roll for all the players and update their fields
			for character in characters:
				if (initiative[1] == 1):
					ego = character[3]
				else:
					ego = 0
				result = roll(character[2], ego) #Dice, ego
				character += (result["successes"], result["triggers"], result["ones"])

			successDict = sortCharactersBySuccesses(characters)
			await context.send(successDict)
			maxVal = -1
			for val in successDict:
				if val > maxVal:
					maxVal = val
				cursor.execute("REPLACE INTO initiative_values(channel_id, value) VALUES(?,?)", (val, context.channel.id,))
				for character in successDict[val]:
					cursor.execute("REPLACE INTO characters(num_successes, num_triggers, num_ones) VALUES(?,?,?) WHERE channel_id=?", (character[4], character[5], character[6], context.channel.id,))
			connection.commit()
			cur_initiative = maxVal
			#update the round number and the cur_initiative in initiatives
			#commit it

		# Do the round
		cursor.execute("SELECT mention, name, num_ego, num_successes, num_triggers FROM characters WHERE channel_id=? AND num_successes=?", (context.channel.id, cur_initiative))
		characters = cursor.fetchall()
		msg += "Round " + str(roundNum) +":\n"
		for character in characters:
			msg += character[0] + ", it is " + (character[1] + "\'s turn." if character[1] else "your turn.")
			extraActions = floor(character[4]/2)
			if (extraActions > 0 or (initiative[1] == 1 and character[2])):
				msg += "You have "
			if (extraActions > 0):
				msg += str(extraActions) + " extra actions"
			if (extraActions > 0 and initiative[1] == 1 and character[2]):
				msg += " and "
			if (initiative[1] == 1 and character[2]):
				msg += str(character[2]) + " extra dice for your first action (from ego)\n"
		# update the round number
		await context.send(msg)

	except Exception as e:
			await context.send("An error occurred while moving to next initiative")
			await context.send(e)


def sortCharactersBySuccesses(characters):
	dict = {}
	for character in characters:
		if (character[4] in dict):
			dict[character[4]] += character
		else:
			dict[character[4]] = [character]
	return dict



@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name)


bot.run(TOKEN)
