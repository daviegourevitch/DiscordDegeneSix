# Work with Python 3.6
import numpy as np
import os
import discord
from discord.ext.commands import Bot, when_mentioned_or

BOT_PREFIX = ("!")
TOKEN = os.environ.get('TOKEN') # Get at discordapp.com/developers/applications/me
print("Current token: " + TOKEN)

bot = Bot(command_prefix=when_mentioned_or(*BOT_PREFIX))

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
        result = ('*Success!* <:degenesis:484759543423696896>\n' if successes >= difficulty else "Failure!\n") if ones <= successes else '*It\'s a botch!* :skull:\n'        
        msg = "%s needs %d successes and rolls:" % (context.author.mention,difficulty) if autos == 0 else "%s needs %d successes, already has %d automatic and rolls:" % (context.author.mention,difficulty,autos)
    else:
        result = '' if ones <= successes else '*It\'s a botch!* :skull:\n'
        msg = "%s rolls:" % (context.author.mention) if autos == 0 else "%s has %d automatic successes and rolls:" % (context.author.mention, autos)
    msg+= " \n %s \n %d successes, %d triggers \n %s" % (', '.join(map(str,roll)),
    successes,
    triggers,
    result)
    await context.send(msg)

   

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name)

bot.run(TOKEN)
