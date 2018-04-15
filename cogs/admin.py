from discord.ext import commands
from .func import checks


class Admin:
    def __init__(self, bot):
        self.bot = bot

    @checks.is_owner()
    @commands.command(hidden=True)
    async def unload(self, extension_name):
        """Unload a cog."""
        self.bot.unload_extension(extension_name)
        await self.bot.say('"{}" unloaded.'.format(extension_name))

    @checks.is_owner()
    @commands.command(hidden=True)
    async def load(self, extension_name):
        """Load a cog."""
        try:
            self.bot.load_extension(extension_name)
        except (ImportError, AttributeError):
            await self.bot.say('"{}" not found.'.format(extension_name))
            return
        await self.bot.say('"{}" loaded.'.format(extension_name))

    @checks.is_owner()
    @commands.command(hidden=True)
    async def list(self):
        """List cogs."""
        await self.bot.say("Currently loaded: " + ", ".join(self.bot.cogs.keys()))

    @checks.is_owner()
    @commands.command(hidden=True)
    async def die(self):
        """Kill bot."""
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
