from discord.ext import commands


def is_owner_bool(ctx):
    return ctx.message.author.id == 196391063987027969


def is_owner():
    def p(ctx):
        return is_owner_bool(ctx)
    return commands.check(p)
