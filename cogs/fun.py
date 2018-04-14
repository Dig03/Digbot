from discord.ext import commands
import random


class Fun:
    """Commands for fun purposes. Allows for provision of infinite quantities of entertainment."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, dice):
        """Roll NdN di(c)e."""
        try:
            count, sides = map(int, dice.split('d'))
        except ValueError:
            await self.bot.say("Format must be NdN.")
            return
        if count > 100 or sides > 1000:
            await self.bot.say("Too many dice or sides.")
            return
        result = ', '.join(str(random.randint(1, sides)) for _ in range(count))
        await self.bot.say(result)

    @commands.command()
    async def roulette(self):
        """Play Russian Roulette."""
        if random.random() <= 1 / 6:
            await self.bot.say("""```
BBBBBBBBBBBBBBBBB               AAA               NNNNNNNN        NNNNNNNN        GGGGGGGGGGGGG
B::::::::::::::::B             A:::A              N:::::::N       N::::::N     GGG::::::::::::G
B::::::BBBBBB:::::B           A:::::A             N::::::::N      N::::::N   GG:::::::::::::::G
BB:::::B     B:::::B         A:::::::A            N:::::::::N     N::::::N  G:::::GGGGGGGG::::G
  B::::B     B:::::B        A:::::::::A           N::::::::::N    N::::::N G:::::G       GGGGGG
  B::::B     B:::::B       A:::::A:::::A          N:::::::::::N   N::::::NG:::::G
  B::::BBBBBB:::::B       A:::::A A:::::A         N:::::::N::::N  N::::::NG:::::G
  B:::::::::::::BB       A:::::A   A:::::A        N::::::N N::::N N::::::NG:::::G    GGGGGGGGGG
  B::::BBBBBB:::::B     A:::::A     A:::::A       N::::::N  N::::N:::::::NG:::::G    G::::::::G
  B::::B     B:::::B   A:::::AAAAAAAAA:::::A      N::::::N   N:::::::::::NG:::::G    GGGGG::::G
  B::::B     B:::::B  A:::::::::::::::::::::A     N::::::N    N::::::::::NG:::::G        G::::G
  B::::B     B:::::B A:::::AAAAAAAAAAAAA:::::A    N::::::N     N:::::::::N G:::::G       G::::G
BB:::::BBBBBB::::::BA:::::A             A:::::A   N::::::N      N::::::::N  G:::::GGGGGGGG::::G
B:::::::::::::::::BA:::::A               A:::::A  N::::::N       N:::::::N   GG:::::::::::::::G
B::::::::::::::::BA:::::A                 A:::::A N::::::N        N::::::N     GGG::::::GGG:::G
BBBBBBBBBBBBBBBBBAAAAAAA                   AAAAAAANNNNNNNN         NNNNNNN        GGGGGG   GGGG
    ```""")
        else:
            await self.bot.say("click")


def setup(bot):
    bot.add_cog(Fun(bot))
