from discord.ext import commands
import time
from urllib.error import HTTPError
from wordnik import WordApi, swagger
import urbandict
from collections import OrderedDict
from .func import paginator, util


class Utility(commands.Cog, name="Utility"):
    """Commands which are potentially useful but do not fall into other categories."""

    def __init__(self, bot):
        self.bot = bot
        self.word_api = WordApi.WordApi(swagger.ApiClient(bot.tokens['wordnik'], 'http://api.wordnik.com/v4'))

    @commands.command()
    async def echo(self, ctx, *, text):
        """Repeat given text back to the user."""
        await ctx.send("".join(text))

    @commands.command()
    async def get_time(self, ctx):
        """Get the current local time of the bot."""
        await ctx.send(time.strftime("It is %a, %d %b %Y %H:%M:%S", time.localtime()))

    @commands.command()
    async def reverse(self, ctx, *, text):
        """Reverse some text."""
        text = text.split()
        rev_text = []
        for word in text[::-1]:
            if word.startswith(':') and word.endswith(':') or word.startswith('<') and word.endswith('>'):
                rev_text.append(word)
            else:
                rev_text.append(word[::-1])
        await ctx.send(' '.join(rev_text))

    @commands.command()
    async def urban(self, ctx, *, word):
        """Get urban dictionary definitions."""
        try:
            definitions = urbandict.define(word)
            definition_string = ""
            pos = 1
            for definition in definitions:
                text = definition["def"]
                example = definition["example"]
                definition_string += '{}:\n{}\n'.format(pos, text)
                if len(example) != 0:
                    definition_string += '\n\tFor example:\n\n{}.\n\n'.format(example)
                pos += 1
            for page in paginator.paginate(definition_string, 2000, '```', '```'):
                await ctx.send(page)
        except HTTPError:
            await ctx.send("No Urban Dictionary definition found.")

    @commands.command()
    async def define(self, ctx, *, word):
        """Get dictionary definitions of words."""
        word = word.lower()
        definitions = self.word_api.getDefinitions(word, sourceDictionaries='wiktionary')
        if definitions is None:
            definitions = self.word_api.getDefinitions(word, sourceDictionaries='ahd')
        if definitions is None:
            await ctx.send("No definition found.")
        else:
            parts_of_speech = util.uniques([d.partOfSpeech for d in definitions])
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
            # TODO: Export constants to an import (e.g. message char limit of 2000)
            for page in paginator.paginate(definition_string, 2000, '```', '```'):
                await ctx.send(page)


def setup(bot):
    bot.add_cog(Utility(bot))
