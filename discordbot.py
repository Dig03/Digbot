import re
import inspect
from collections import OrderedDict


class Bunch:

    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class Bot:

    def __init__(self, prefix, client, owner_id='0'):
        self.prefix = prefix
        self.client = client
        self.owner_id = owner_id
        self.commands = OrderedDict()

    def command(self, pass_msg=False):
        def dec(func):
            name = func.__name__
            if name in self.commands:
                raise ValueError('command with name \'{}\' already exists'.format(name))
            if len(inspect.getfullargspec(func).args) == 0 and pass_msg:
                raise ValueError('pass_msg functions must have at least one parameter')
            func.pass_msg = pass_msg
            self.commands[name] = func
        return dec

    def permissions(self, **perms):
        def dec(func):
            if func is None:
                raise SyntaxError('command must be defined before permissions are assigned')
            func.perms = perms
            return func
        return dec

    async def run(self, message):
        self._current_message = message
        content = message.content
        if message.author.bot or content == '':
            return
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

    async def do_func(self, message, command, args):
        if command in self.commands:
            func = self.commands[command]

            if hasattr(func, 'perms'):
                if not self.has_permissions(message, func.perms):
                    await self.insufficient_permissions(message)
                    return

            spec = self.get_func_spec(func)
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

    def has_permissions(self, message, perms):
        if message.author.id == self.owner_id:
            return True
        resolved = message.channel.permissions_for(message.author)
        return all(getattr(resolved, perm, None) == value for perm, value in perms.items())

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
        return self.prefix + func.__name__ + ' ' * bool(spec.req_argc) + str_req_argv + ' ' * bool(spec.opt_argc) + str_opt_argv + doc

    async def say(self, *args, **kwargs):
        await self.client.send_message(self._current_message.channel, *args, **kwargs)

    async def command_not_found(self, message):
        pass

    async def not_enough_args(self, syntax_msg):
        await self.say('```Not enough arguments.\nSyntax: ' + syntax_msg + '```')

    async def insufficient_permissions(self, message):
        await self.say('```You do not have sufficient permissions to run this command.```')
