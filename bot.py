import discord
import asyncio
import traceback
import re
from inspect import getfullargspec
from inspect import iscoroutinefunction
import logging

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


class Commands:

    def __init__(self, prefix, client):
        self.prefix = prefix
        self.client = client
        self.commands = {}

    def reg(self, pass_msg=False):
        def dec(func):
            name = func.__name__
            if name in self.commands:
                raise ValueError('command with name \'{}\' already exists'.format(name))
            if len(getfullargspec(func).args) == 0 and pass_msg:
                raise ValueError('pass_msg functions must have at least one parameter')
            self.commands[name] = (func, pass_msg)
        return dec

    async def command_not_found(self, message):
        pass

    async def not_enough_args(self, message):
        pass

    async def do_func(self, message, command, args):
        if command in self.commands:
            func, pass_msg = self.commands[command][0], self.commands[command][1]
            argspec = getfullargspec(func)

            opt_argc = 0 if argspec.defaults is None else len(argspec.defaults)
            req_argc = 0 if argspec.args is None else len(argspec.args) - opt_argc
            if pass_msg:
                req_argc -= 1

            if req_argc > len(args):
                await self.not_enough_args(message)
                return

            if req_argc + opt_argc < len(args):
                args = args[:req_argc + opt_argc]

            if pass_msg:

                if iscoroutinefunction(func):
                    await func(message, *args)
                else:
                    func(message, *args)

            else:

                if iscoroutinefunction(func):
                    await func(*args)
                else:
                    func(*args)

        else:
            await self.command_not_found

    async def run(self, message):
        content = message.clean_content
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

# COMMANDS

cmds = Commands('`', client)
@cmds.reg(pass_msg=True)
async def echo(msg, txt):
    await client.send_message(msg.channel, txt)

@cmds.reg()
async def die():
    main_logger.info('Gracefully terminated by request.')
    await client.logout()

@cmds.reg(pass_msg=True)
async def sillyecho(msg, txt='hurr durr'):
    await client.send_message(msg.channel, txt)

# COMMANDS

@client.event
async def on_ready():
    main_logger.info('Logged in as {}, with ID {}'.format(client.user.name, client.user.id))

@client.event
async def on_error(event, *args, **kwargs):
    main_logger.error(traceback.format_exc())

@client.event
async def on_message(message):
    await cmds.run(message)

with open('token', 'r') as f:
    token = f.read()
client.run(token)
