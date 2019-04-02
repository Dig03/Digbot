from discord.ext import commands
from .func import checks


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_owner()
    @commands.command(hidden=True)
    async def unload(self, ctx, extension_name):
        """Unload a cog."""
        self.bot.unload_extension(extension_name)
        await ctx.send('"{}" unloaded.'.format(extension_name))

    @checks.is_owner()
    @commands.command(hidden=True)
    async def load(self, ctx, extension_name):
        """Load a cog."""
        try:
            self.bot.load_extension(extension_name)
        except (ImportError, AttributeError):
            await ctx.send('"{}" not found.'.format(extension_name))
            return
        await ctx.send('"{}" loaded.'.format(extension_name))

    @checks.is_owner()
    @commands.command(hidden=True)
    async def list(self, ctx):
        """List cogs."""
        await ctx.send("Currently loaded: " + ", ".join(self.bot.cogs.keys()))

    @checks.is_owner()
    @commands.command(hidden=True)
    async def die(self, ctx):
        """Kill bot."""
        await ctx.send("Shutting down.")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
