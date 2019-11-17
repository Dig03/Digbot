from discord.ext import commands


class Server(commands.Cog, name="Server"):
    """Utility commands specifically relating to server functions."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clean(self, ctx, count: int):
        """Delete <count> messages."""
        deleted = await ctx.channel.purge(limit=count, before=ctx.message)
        msg = await ctx.send("Successfully deleted {} message{}.".format(len(deleted),
                                                                         's' if len(deleted) > 1 else ''))
        await msg.delete(delay=2)


def setup(bot):
    bot.add_cog(Server(bot))
