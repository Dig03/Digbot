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
    async def set(self, ctx, key, *, val=None):
        """Set configuration values. If val not given, set to default."""
        try:
            if val is not None:
                self.bot.config.set_val(key, val)
                await ctx.send("{} has been updated.".format(key))
            else:
                self.bot.config.update_default(key)
                await ctx.send("{} has been set to default.".format(key))
        except KeyError:
            await ctx.send("Key not found.")
        except (TypeError, ValueError):
            await ctx.send("Invalid type. Was expecting {}.".format(self.bot.config.get_type(key).__name__))

    @commands.command(hidden=True)
    async def list_config(self, ctx):
        """List configuration values."""
        result = ""
        cfg = self.bot.config.config_store
        for key in cfg:
            result += '{} = {}\n'.format(key, self.bot.config.get_val(key))
        await ctx.send(result)


def setup(bot):
    bot.add_cog(Config(bot))
