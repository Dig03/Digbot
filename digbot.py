import discord
import discordbot
import asyncio
import time
import os
import logging
from wordnik import *
from random import randint
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


client = discord.Client()
bot = discordbot.Bot('!', client, '196391063987027969')


@bot.command()
async def echo(text):
    """Repeat given text back to user."""
    await bot.say(text)


@bot.command()
async def help(command='all'):
    """List available commands."""
    if command == 'all':
        syntax_msgs = []
        for func in bot.commands.values():
            syntax_msgs.append(bot.get_syntax_msg(func))
        await bot.say('```' + 'Syntax: `command (required arg) [optional arg=default value]\n\n' + '\n'.join(syntax_msgs) + '```')
    else:
        if command in bot.commands:
            await bot.say('```\n' + bot.get_syntax_msg(bot.commands[command]) + '```')
        else:
            await bot.say('```Command not found.```')


@bot.command()
async def gettime():
    """Get the current local time of the bot."""
    await bot.say(time.strftime('It is %a, %d %b %Y %H:%M:%S.', time.localtime()))


@bot.command()
async def roulette():
    """Play Russian Roulette."""
    global roulette_counter
    if randint(1, 6) == 6 or roulette_counter == 6:
        roulette_counter = 0
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
        roulette_counter += 1
        await bot.say('click')
roulette_counter = 0


@bot.command()
async def dice(count=1, sides=6):
    """Roll (a) di(e/ce)."""
    try:
        sides = int(sides)
        count = int(count)
    except ValueError:
        await bot.say('Invalid arguments, make sure both are numbers.')
    else:
        if sides < 1:
            await bot.say('Invalid number of sides.')
        elif count < 1:
            await bot.say('Invalid number of dice.')
        elif count > 100 or sides > 100:
            await bot.say('Too many dice or sides, please try with numbers at or below 100.')
        else:
            dice = [str(randint(1, sides)) for _ in range(count)]
            await bot.say(' '.join(dice))


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
        await bot.say('**No definition found.**')
    else:
        partsofspeech = uniques([d.partOfSpeech for d in definitions])
        parsed_defs = OrderedDict()
        for partofspeech in partsofspeech:
            parsed_defs[partofspeech] = []
        for definition in definitions:
            parsed_defs[definition.partOfSpeech].append(definition.text)
        definition_string = ''
        for partofspeech in parsed_defs:
            definition_string += '{}:\n'.format(partofspeech.replace('-', ' '))
            pos = 1
            for text in parsed_defs[partofspeech]:
                definition_string += '\t{}. {}\n'.format(pos, text)
                pos += 1
        await bot.say('```' + definition_string + '```')


@client.event
async def on_ready():
    main_logger.info('Logged in as {}, with ID {}'.format(client.user.name, client.user.id))
    await client.change_presence(game=discord.Game(name='Type !help'))


@client.event
async def on_error(event, *args, **kwargs):
    if exc_info()[0] is discord.errors.HTTPException:
        await bot.say('**Unable to process command, the response text is >2000 characters.**')
    else:
        main_logger.error(format_exc())
        if event == 'on_message':
            message = args[0]
            main_logger.error('Message content: ' + message.content)
            await bot.say('**An internal error occured. This event has been automatically logged.**')


@client.event
async def on_message(message):
    await bot.run(message)

tokens = {}
tokens['discord'] = os.getenv('discord')
tokens['wordnik'] = os.getenv('wordnik')
if None in tokens.values():
    raise EnvironmentError('tokens missing, cannot launch')

wordApi = WordApi.WordApi(swagger.ApiClient(tokens['wordnik'], 'http://api.wordnik.com/v4'))
client.run(tokens['discord'])
