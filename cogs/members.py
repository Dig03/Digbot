import discord
from discord.ext import commands


class Members(commands.Cog, name="Members"):
    """Commands for pulling data relevant to members."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whois(self, ctx, member: discord.Member = None):
        """Dumps information on a user. Target must be a mention."""
        if member is None:
            member = ctx.message.author
        embed = discord.Embed(title="Details for {}".format(member.name), colour=int('37d17f', 16))
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='Name', value=member.name, inline=False)
        embed.add_field(name='Discriminator', value=member.discriminator, inline=False)
        embed.add_field(name='ID', value=member.id, inline=False)
        embed.add_field(name='Bot', value='Yes' if member.bot else 'No', inline=False)
        embed.add_field(name='Avatar URL', value=member.avatar_url if not '' else member.default_avatar_url,
                        inline=False)
        embed.add_field(name='Creation time', value=member.created_at, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Members(bot))
