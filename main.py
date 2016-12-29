import discord
from discord.ext import commands
import asyncio
import traceback
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
"""
 -- LOGGING TO FILES IS DISABLED FOR NOW --
fh = logging.FileHandler("log_filename.txt")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
"""
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

bot = commands.Bot(command_prefix="`")

# HELPER FUNCTIONS

def log_message(msg):
    servname = "(N/A)" if msg.server == None else msg.server.name
    if isinstance(msg.channel, discord.PrivateChannel):
        channame = "(DM) [{}]".format(','.join([str(u) for u in msg.channel.recipients]))
    else:
        channame = msg.channel.name
    logging.info("'{}'@'{}', {} | {}: {}".format(servname, channame, msg.timestamp, str(msg.author), msg.clean_content))

async def check_admin(usr):
    if usr == await bot.get_user_info("196391063987027969"):
        return True
    else:
        return False

# HELPER FUNCTIONS

# EVENTS

@bot.event
async def on_ready():
    logger.info("Logged in as {}, with ID {}".format(bot.user.name, bot.user.id))

@bot.event
async def on_error(event, *args, **kwargs):
    logging.error(traceback.format_exc())

@bot.event
async def on_message(msg):
    log_message(msg)
    await bot.process_commands(msg)

# EVENTS

# COMMANDS

@bot.command()
async def echo(*, msg: str):
    await bot.say(msg)

@bot.command(pass_context=True)
async def die(ctx):
    if await check_admin(ctx.message.author):
        logging.info("Shutting down by admin request.")
        await bot.logout()

# COMMANDS

with open("token", "r") as tf:
    token = tf.read()
bot.run(token)
