from discord.ext import commands
from .func import paginator
import random
from math import isclose
import asyncio


class Fun(commands.Cog, name="Fun"):
    """Commands for fun purposes. Allows for provision of infinite quantities of entertainment."""

    def __init__(self, bot):
        self.bot = bot
        self.roulette_sum = 0

    @commands.command()
    async def roll(self, ctx, dice):
        """Roll NdN di(c)e."""
        try:
            count, sides = map(int, dice.split('d'))
            if count > self.bot.config.dice_count_lim or sides > self.bot.config.dice_sides_lim:
                await ctx.send("Too many dice or sides.")
            else:
                numbers = []

                async def randint_str(a, b):
                    return str(random.randint(a, b))
                for _ in range(count):
                    numbers.append(await randint_str(1, sides))
                result = ', '.join(numbers)
                for page in paginator.paginate(result, 2000):
                    await ctx.send(page)
        except ValueError:
            await ctx.send("Format must be NdN where each N is an integer.")

    @commands.command()
    async def roulette(self, ctx):
        """Play Russian Roulette."""
        chance = self.bot.config.roulette_prob
        should_fire = self.roulette_sum + chance
        if random.random() <= chance or isclose(should_fire, 1) or should_fire >= 1:
            self.roulette_sum = 0
            await ctx.send("""```
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
            self.roulette_sum += chance
            await ctx.send("click".format(self.roulette_sum))

    @commands.command()
    async def guess(self, ctx, imin: int, imax: int, tries: int = 3):
        """What number am I thinking of?"""
        already = []

        if imax < 0 or imin < 0 or imin > imax:
            await ctx.send("That doesn't make sense.")
        elif imax - imin < tries:
            await ctx.send("That's too easy.")
        else:
            i = random.randint(imin, imax)
            await ctx.send("I've got a number, what's your guess?")

            t = tries
            while t > 0:
                try:
                    def predicate(msg):
                        return msg.author == ctx.message.author and msg.channel == ctx.message.channel

                    guess = int((await self.bot.wait_for("message", check=predicate, timeout=30)).content)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out while waiting for a response.")
                    break
                except ValueError:
                    await ctx.send("That isn't a number.")
                else:
                    if guess in already:
                        await ctx.send("You've already tried that.")
                    elif i == guess:
                        await ctx.send("Correct. Good job.")
                        break
                    else:
                        t -= 1
                        already.append(guess)
                        await ctx.send("Wrong. You have {} tr{} left.".format(t, 'ies' if t != 1 else 'y'))

            await ctx.send("The number was {}.".format(i))


def setup(bot):
    bot.add_cog(Fun(bot))
