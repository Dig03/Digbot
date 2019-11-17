from discord.ext import commands


class Server(commands.Cog, name="Server"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("Hello, world!")


def setup(bot):
    bot.add_cog(Server(bot))
