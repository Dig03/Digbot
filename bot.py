import discord
from discord.ext import commands
import asyncio
import logging
import time
import random
from os import getenv
from wordnik import *
from collections import OrderedDict

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


# COMMANDS


@bot.command()
async def echo(text):
    """Repeat given text back to user."""
    await bot.say(text)


@bot.command()
async def gettime():
    """Get the current local time of the bot."""
    await bot.say(time.strftime("It is %a, %d %b %Y %H:%M:%S", time.localtime()))


@bot.command()
async def roulette():
    """Play Russian Roulette."""
    if random.random() <= 1/6:
        await bot.say("""```
BBBBBBBBBBBBBBBBB               AAA               NNNNNNNN        NNNNNNNN        GGGGGGGGGGGGG
B::::::::::::::::B             A:::A              N:::::::N       N::::::N     GGG::::::::::::G
B::::::BBBBBB:::::B           A:::::A             N::::::::N      N::::::N   GG:::::::::::::::G
BB:::::B     B:::::B         A:::::::A            N:::::::::N     N::::::N  G:::::GGGGGGGG::::G
  B::::B     B:::::B        A:::::::::A           N::::::::::N    N::::::N G:::::G       GGGGGG
  B::::B     B:::::B       A:::::A:::::A          N:::::::::::N   N::::::NG:::::G
  B::::BBBBBB:::::B       A:::::A A:::::A         N:::::::N::::N  N::::::NG:::::G
  B:::::::::::::BB       A:::::A   A:::::A        N::::::N N::::N N::::::NG:::::G    GGGGGGGGGG
  B::::BBBBBB:::::B     A:::::A     A:::::A       N::::::N  N::::N:::::::NG:::::G    G::::::::G
  B::::B     B:::::B   A:::::AAAAAAAAA:::::A      N::::::N   N:::::::::::NG:::::G    GGGGG::::G
  B::::B     B:::::B  A:::::::::::::::::::::A     N::::::N    N::::::::::NG:::::G        G::::G
  B::::B     B:::::B A:::::AAAAAAAAAAAAA:::::A    N::::::N     N:::::::::N G:::::G       G::::G
BB:::::BBBBBB::::::BA:::::A             A:::::A   N::::::N      N::::::::N  G:::::GGGGGGGG::::G
B:::::::::::::::::BA:::::A               A:::::A  N::::::N       N:::::::N   GG:::::::::::::::G
B::::::::::::::::BA:::::A                 A:::::A N::::::N        N::::::N     GGG::::::GGG:::G
BBBBBBBBBBBBBBBBBAAAAAAA                   AAAAAAANNNNNNNN         NNNNNNN        GGGGGG   GGGG```""")
    else:
        await bot.say("click")


@bot.command()
async def roll(dice):
    """Roll NdN di(c)e."""
    try:
        count, sides = map(int, dice.split('d'))
    except ValueError:
        await bot.say("Format must be NdN.")
        return
    if count > 100 or sides > 1000:
        await bot.say("Too many dice or sides.")
        return
    result = ', '.join(str(random.randint(1, sides)) for _ in range(count))
    await bot.say(result)


def uniques(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def page(string, length):
    return [string[start:start + length] for start in range(0, len(string), length)]


@bot.command()
async def define(word):
    """Get dictionary definitions of words."""
    word = word.lower()
    definitions = wordApi.getDefinitions(word, sourceDictionaries='wiktionary')
    if definitions is None:
        definitions = wordApi.getDefinitions(word, sourceDictionaries='ahd')
    if definitions is None:
        await bot.say("No definition found.")
    else:
        parts_of_speech = uniques([d.partOfSpeech for d in definitions])
        parsed_defs = OrderedDict()
        for part_of_speech in parts_of_speech:
            parsed_defs[part_of_speech] = []
        for definition in definitions:
            parsed_defs[definition.partOfSpeech].append(definition.text)
        definition_string = ''
        for part_of_speech in parsed_defs:
            definition_string += '{}:\n'.format(part_of_speech.replace('-', ' '))
            pos = 1
            for text in parsed_defs[part_of_speech]:
                definition_string += '\t{}. {}\n'.format(pos, text)
                pos += 1
        if len(definition_string) + 6 > 2000:
            paged = page(definition_string, 1994)
            for string in paged:
                await bot.say("```{}```".format(string))
        else:
            await bot.say("```{}```".format(definition_string))


tokens = {'discord': getenv('discord'), 'wordnik': getenv('wordnik')}
if None in tokens.values():
    raise EnvironmentError('Tokens missing, cannot launch.')

wordApi = WordApi.WordApi(swagger.ApiClient(tokens['wordnik'], 'http://api.wordnik.com/v4'))
bot.run(tokens['discord'])
