from discord.ext import commands
from .func import checks


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return checks.is_owner_bool(ctx)

    @commands.command(hidden=True)
    async def unload(self, ctx, extension_name):
        """Unload a cog."""
        if extension_name == self.__class__.__module__:
            await ctx.send("Cannot unload essential cog.")
        else:
            try:
                self.bot.unload_extension(extension_name)
                await ctx.send('"{}" unloaded.'.format(extension_name))
            except commands.ExtensionNotLoaded:
                await ctx.send('Can\'t find "{}".'.format(extension_name))

    @commands.command(hidden=True)
    async def load(self, ctx, extension_name):
        """Load a cog."""
        try:
            self.bot.load_extension(extension_name)
            await ctx.send('"{}" loaded.'.format(extension_name))
        except commands.ExtensionNotFound:
            await ctx.send('"{}" not found.'.format(extension_name))
        except commands.ExtensionAlreadyLoaded:
            await ctx.send('"{}" is already loaded.'.format(extension_name))

    @commands.command(hidden=True)
    async def list(self, ctx):
        """List cogs."""
        import_locations = []
        for cog in self.bot.cogs.values():
            import_locations.append(cog.__class__.__module__)
        await ctx.send("Currently loaded: " + ", ".join(import_locations))

    @commands.command(hidden=True)
    async def die(self, ctx):
        """Kill bot."""
        await ctx.send("Shutting down.")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
