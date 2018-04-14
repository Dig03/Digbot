from discord.ext import commands
import time
from wordnik import WordApi, swagger
from collections import OrderedDict


def page(string, length):
    return [string[start:start + length] for start in range(0, len(string), length)]


def uniques(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


class Utility:
    """Commands which are potentially useful but do not fall into other categories."""

    def __init__(self, bot):
        self.bot = bot
        self.word_api = WordApi.WordApi(swagger.ApiClient(bot.tokens['wordnik'], 'http://api.wordnik.com/v4'))

    @commands.command()
    async def echo(self, text):
        """Repeat given text back to the user."""
        await self.bot.say(text)

    @commands.command()
    async def get_time(self):
        """Get the current local time of the bot."""
        await self.bot.say(time.strftime("It is %a, %d %b %Y %H:%M:%S", time.localtime()))

    @commands.command()
    async def define(self, word):
        """Get dictionary definitions of words."""
        word = word.lower()
        definitions = self.word_api.getDefinitions(word, sourceDictionaries='wiktionary')
        if definitions is None:
            definitions = self.word_api.getDefinitions(word, sourceDictionaries='ahd')
        if definitions is None:
            await self.bot.say("No definition found.")
        else:
            parts_of_speech = uniques([d.partOfSpeech for d in definitions])
            parsed_defs = OrderedDict()
            for part_of_speech in parts_of_speech:
                parsed_defs[part_of_speech] = []
            for definition in definitions:
                parsed_defs[definition.partOfSpeech].append(definition.text)
            definition_string = ''
            for part_of_speech in parsed_defs:
                definition_string += '{}:\n'.format(part_of_speech.replace('-', ' '))
                pos = 1
                for text in parsed_defs[part_of_speech]:
                    definition_string += '\t{}. {}\n'.format(pos, text)
                    pos += 1
            if len(definition_string) + 6 > 2000:
                paged = page(definition_string, 1994)
                for string in paged:
                    await self.bot.say("```{}```".format(string))
            else:
                await self.bot.say("```{}```".format(definition_string))


def setup(bot):
    bot.add_cog(Utility(bot))
