from discord.ext import commands
from .func import checks


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return checks.is_owner_bool(ctx)

    @commands.command(hidden=True)
    async def get(self, ctx, key):
        """Get configuration values."""
        try:
            # TODO: Paginate this?
            await ctx.send("{} = {}".format(key, self.bot.config.key))
        except KeyError:
            await ctx.send("Key not found.")

    @commands.command(hidden=True)
    async def set(self, ctx, key, *, val):
        """Set configuration values."""
        try:
            self.bot.config.set_key(key, val)
            await ctx.send("{} has been updated.".format(key))
        except KeyError:
            await ctx.send("Key not found.")
        except TypeError:
            await ctx.send("Invalid type. Was expecting {}.".format(self.bot.config.get_type(key)))

    @commands.command(hidden=True)
    async def list_config(self, ctx):
        """List configuration values."""
        result = ""
        cfg = self.bot.config.config_store
        for key in cfg:
            result += '{} = {}\n'.format(key, cfg[key])
        await ctx.send(result)


def setup(bot):
    bot.add_cog(Config(bot))
