import discord
from discord.ext import commands
import asyncio
import traceback
import logging
import random

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s: %(message)s')
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
d_ch = logging.StreamHandler()
d_ch.setLevel(logging.ERROR)
d_ch.setFormatter(formatter)
discord_logger.addHandler(d_ch)

bot = commands.Bot(command_prefix='`', description='Test message.')

# HELPER FUNCTIONS


def log_message(msg):
    if msg.author != bot.user:
        servname = '(N/A)' if msg.server is None else msg.server.name
        if isinstance(msg.channel, discord.PrivateChannel):
            channame = '(DM) [{}]'.format(','.join([str(u) for u in msg.channel.recipients]))
        else:
            channame = msg.channel.name
        logger.info('\'{}\'@\'{}\', {} | {}: {}'.format(servname, channame, msg.timestamp, str(msg.author), msg.clean_content))


# NOTE: this scheme is used if the checking function is required outside the decorator (e.g., in another checking function)
"""
(this is the usual scheme)
def is_me():
    def predicate(ctx):
        return ctx.message.author.id == 'my-user-id'
    return commands.check(predicate)
@bot.command()
@is_me()
async def only_me():
    await bot.say('Only you!')
"""


def is_owner_check(msg):
    return msg.author.id == '196391063987027969'


def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))


# HELPER FUNCTIONS

# EVENTS


@bot.event
async def on_ready():
    logger.info('Logged in as {}, with ID {}'.format(bot.user.name, bot.user.id))


@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(traceback.format_exc())


@bot.event
async def on_message(msg):
    log_message(msg)
    await bot.process_commands(msg)


@bot.event
async def on_command_error(error, ctx):
    logger.info(error)


# EVENTS

# COMMANDS


@bot.command()
async def echo(*, msg: str):
    await bot.say(msg)


@bot.command()
async def hello():
    await bot.say(random.choice(['Hello!', 'Hey there!', 'Hey.', 'Salutation!']))


@bot.command()
@is_owner()
async def die():
    logger.info('Shutting down by admin request.')
    await bot.logout()


# COMMANDS

with open('token', 'r') as tf:
    token = tf.read()
bot.run(token)
