import discord
from discord.ext import commands
import logging
from os import getenv
import traceback

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


bot = commands.Bot(command_prefix=',', description="A shitty bot.")


@bot.event
async def on_ready():
    logger.info("Ready! Username: {}, ID: {}.".format(bot.user.name, bot.user.id))
    await bot.change_presence(activity=discord.Game(name="Type {}help".format(bot.command_prefix)))


@bot.event
async def on_error(event, *args, **kwargs):
    logger.error("Encountered internal error:")
    logger.error(traceback.format_exc())
    logger.error("During event:")
    logger.error(event)
    logger.error("With args & kwargs:")
    logger.error("args: {}; kwargs: {}".format(args, kwargs))


@bot.event
async def on_command_error(exception, ctx):
    logger.error("Encountered command exception:")
    logger.error(exception)
    logger.error("This is as a result of the message:")
    logger.error(ctx.message.content)
    logger.error('By user "{0}" with ID {0.id}'.format(ctx.message.author))


bot.tokens = {'discord': getenv('discord'), 'wordnik': getenv('wordnik')}
if None in bot.tokens.values():
    raise EnvironmentError('Tokens missing, cannot launch.')

extensions = ('cogs.utility', 'cogs.fun', 'cogs.members', 'cogs.admin')

for extension in extensions:
    bot.load_extension(extension)

bot.run(bot.tokens['discord'])
