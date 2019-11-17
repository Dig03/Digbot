import discord
from discord.ext import commands
from cogs.func import config
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


bot = commands.Bot(command_prefix='.', description="A shitty bot.")


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
async def on_command_error(ctx, exception):
    logger.error("Encountered command exception.")
    logger.error("Message: \"{0}\" by user {1} with ID {1.id}".format(ctx.message.content, ctx.message.author))
    logger.error("=== EXCEPTION ===")
    logger.error("".join(traceback.format_exception(type(exception), exception, exception.__traceback__)))


bot.tokens = {'discord': getenv('discord'), 'wordnik': getenv('wordnik')}
if None in bot.tokens.values():
    raise EnvironmentError('Tokens missing, cannot launch.')

extensions = ('cogs.utility', 'cogs.fun', 'cogs.members', 'cogs.admin', 'cogs.config', 'cogs.server')

for extension in extensions:
    bot.load_extension(extension)

bot.config = config

bot.run(bot.tokens['discord'])
