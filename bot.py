import discord
from discord.ext import commands
import asyncio
import time
import os
import logging
import random
from wordnik import *
from collections import OrderedDict
from traceback import format_exc
from sys import exc_info

main_logger = logging.getLogger('main')
main_logger.setLevel(logging.INFO)
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s: %(message)s')

main_console = logging.StreamHandler()
main_console.setLevel(logging.INFO)
main_console.setFormatter(formatter)
main_logger.addHandler(main_console)

discord_console = logging.StreamHandler()
discord_console.setLevel(logging.ERROR)
discord_console.setFormatter(formatter)
discord_logger.addHandler(discord_console)

bot = commands.Bot(command_prefix='`', description='A shitty bot.', command_not_found='Command {} not found.')


@bot.event
async def on_ready():
    main_logger.info('Logged in as {}, with ID {}'.format(bot.user.name, bot.user.id))
    await bot.change_presence(game=discord.Game(name='Type `help'))


@bot.event
async def on_error(event, *args, **kwargs):
    if exc_info()[0] is discord.errors.HTTPException:
        await bot.say('Unable to process command, the response text is >2000 characters.')
    else:
        main_logger.error(format_exc())
        if event == 'on_message':
            message = args[0]
            main_logger.error('Message content: ' + message.content)
            await bot.say('An internal error occured. This event has been automatically logged.')


@bot.command()
async def echo(text):
    """Repeat given text back to user."""
    await bot.say(text)


@bot.command()
async def gettime():
    """Get the current local time of the bot."""
    await bot.say(time.strftime('It is %a, %d %b %Y %H:%M:%S.', time.localtime()))


@bot.command()
async def roulette():
    """Play Russian Roulette."""
    if random.random() <= 0.1666:
        await bot.say('''```
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
BBBBBBBBBBBBBBBBBAAAAAAA                   AAAAAAANNNNNNNN         NNNNNNN        GGGGGG   GGGG```''')
    else:
        await bot.say('click')


@bot.command()
async def roll(dice):
    """Roll an NdN dice."""
    try:
        count, sides = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format must be NdN.')
        return

    if count > 100 or sides > 1000:
        await bot.say('Too many dice or sides.')
        return

    result = ', '.join(str(random.randint(1, sides)) for r in range(count))
    await bot.say(result)


def uniques(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


@bot.command()
async def define(word):
    """Get dictionary definitions of words."""
    word = word.lower()
    definitions = wordApi.getDefinitions(word, sourceDictionaries='wiktionary')
    if definitions is None:
        definitions = wordApi.getDefinitions(word, sourceDictionaries='ahd')
    if definitions is None:
        await bot.say('No definition found.')
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
        await bot.say('```' + definition_string + '```')


tokens = {}
tokens['discord'] = os.getenv('discord')
tokens['wordnik'] = os.getenv('wordnik')
if None in tokens.values():
    raise EnvironmentError('tokens missing, cannot launch')

wordApi = WordApi.WordApi(swagger.ApiClient(tokens['wordnik'], 'http://api.wordnik.com/v4'))
bot.run(tokens['discord'])
