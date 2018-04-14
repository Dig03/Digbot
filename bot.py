import discord
from discord.ext import commands
import asyncio
import logging
from os import getenv

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s: %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)
discord_logger.addHandler(console)


bot = commands.Bot(command_prefix='.', description="A shitty bot.")


@bot.event
async def on_ready():
    logger.info("Ready! Username: {}, ID: {}.".format(bot.user.name, bot.user.id))
    await bot.change_presence(game=discord.Game(name="Type {}help".format(bot.command_prefix)))


@bot.event
async def on_command_error(exception, context):
    logger.error("Encountered exception: {}, as a result of message: '{}'".format(exception, context.message.content))


bot.tokens = {'discord': getenv('discord'), 'wordnik': getenv('wordnik')}
if None in bot.tokens.values():
    raise EnvironmentError('Tokens missing, cannot launch.')

extensions = ('cogs.utility', 'cogs.fun', 'cogs.members')

for extension in extensions:
    bot.load_extension(extension)

bot.run(bot.tokens['discord'])
