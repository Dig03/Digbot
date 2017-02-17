import discord
import asyncio
import re
import time
import os
import logging
import inspect
from wordnik import *
from collections import OrderedDict
from random import randint
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


class Bunch:

    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class Bot:

    def __init__(self, prefix, client):
        self.prefix = prefix
        self.client = client
        self.commands = OrderedDict()

    def cmd(self, pass_msg=False):
        def dec(func):
            name = func.__name__
            if name in self.commands:
                raise ValueError('command with name \'{}\' already exists'.format(name))
            if len(inspect.getfullargspec(func).args) == 0 and pass_msg:
                raise ValueError('pass_msg functions must have at least one parameter')
            func.pass_msg = pass_msg
            self.commands[name] = func
        return dec

    async def command_not_found(self, message):
        pass

    async def not_enough_args(self, syntax_msg):
        await bot.say('```Not enough arguments.\nSyntax: `' + syntax_msg + '```')

    def get_func_spec(self, func):
        argspec = inspect.getfullargspec(func)
        opt_argc = 0 if argspec.defaults is None else len(argspec.defaults)
        req_argc = 0 if argspec.args is None else len(argspec.args) - opt_argc
        opt_argv = argspec.args[req_argc:]
        if func.pass_msg:
            req_argv = argspec.args[1:req_argc]
        else:
            req_argv = argspec.args[:req_argc]
        if func.pass_msg:
            req_argc -= 1
        defaults = argspec.defaults
        return Bunch(opt_argc=opt_argc,
                     req_argc=req_argc,
                     opt_argv=opt_argv,
                     req_argv=req_argv,
                     defaults=defaults)

    def get_syntax_msg(self, func):
        spec = self.get_func_spec(func)
        str_req_argv = ' '.join(['(' + arg + ')' for arg in spec.req_argv])
        if spec.defaults is None:
            str_opt_argv = ''
        else:
            str_opt_argv = ' '.join(['[{}={}]'.format(arg[0], arg[1]) for arg in zip(spec.opt_argv, spec.defaults)])
        if func.__doc__ is None:
            doc = ''
        else:
            doc = '\n\t' + func.__doc__
        return func.__name__ + ' ' * bool(spec.req_argc) + str_req_argv + ' ' * bool(spec.opt_argc) + str_opt_argv + doc

    async def do_func(self, message, command, args):
        if command in self.commands:
            func = self.commands[command]
            spec = self.get_func_spec(func)
            self._current_message = message

            opt_argc = spec.opt_argc
            req_argc = spec.req_argc

            if req_argc > len(args):
                await self.not_enough_args(self.get_syntax_msg(func))
                return

            if req_argc + opt_argc < len(args):
                args = args[:req_argc + opt_argc]

            if func.pass_msg:

                if inspect.iscoroutinefunction(func):
                    await func(message, *args)
                else:
                    func(message, *args)

            else:

                if inspect.iscoroutinefunction(func):
                    await func(*args)
                else:
                    func(*args)

        else:
            await self.command_not_found(message)

    async def run(self, message):
        content = message.content
        content = content.split(None, 1)
        if content[0].startswith(self.prefix):
            command = content[0][len(self.prefix):]
            if len(content) > 1:
                args = re.findall(r'[^\\"\s]+|(?<!\\)".+?(?<!\\)"', content[1])
                for arg in args:
                    if arg.startswith('"'):
                        args[args.index(arg)] = arg[1:-1]
                await self.do_func(message, command, args)
            else:
                args = []
                await self.do_func(message, command, args)
        else:
            pass

    async def say(self, *args, **kwargs):
        await self.client.send_message(self._current_message.channel, *args, **kwargs)

# COMMANDS


client = discord.Client()
bot = Bot('`', client)


@bot.cmd()
async def echo(text):
    """Repeat given text back to user."""
    await bot.say(text)


@bot.cmd()
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


@bot.cmd()
async def gettime():
    """Get the current local time of the bot."""
    await bot.say(time.strftime('It is %a, %d %b %Y %H:%M:%S.', time.localtime()))


@bot.cmd()
async def roulette():
    """Play Russian Roulette."""
    if randint(1, 6) == 6:
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


@bot.cmd()
async def dice(sides=6, count=1):
    """Role (a) di(e/ce)."""
    try:
        sides = int(sides)
        count = int(count)
    except ValueError:
        await bot.say('Invalid arguments, make sure both are numbers.')
    else:
        if sides < 1:
            await bot.say('Invalid number of sides.')
        else:
            dice = [str(randint(1, sides)) for _ in range(count)]
            await bot.say(' '.join(dice))


def uniques(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


@bot.cmd()
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

# COMMANDS


@client.event
async def on_ready():
    main_logger.info('Logged in as {}, with ID {}'.format(client.user.name, client.user.id))
    await client.change_presence(game=discord.Game(name='Type `help'))


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
