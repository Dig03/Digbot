import discord
import asyncio
import traceback
import colorama
import logging

colorama.init()

class client(discord.Client):

    async def on_ready(self):
        global OWNER 
        OWNER = await self.get_user_info("196391063987027969")
        print("READY")

    async def phone_home(self, msg):
        await self.send_message(OWNER, msg)

    async def on_error(self, event, *args, **kwargs):
        err = traceback.format_exc()
        print(colorama.Fore.RED+err+colorama.Fore.RESET)
        await self.phone_home("```Python\n"+err+"```")

    async def on_message(self, msg):

        # INCOMING MESSAGE LOGGING (TODO: MAKE THIS MORE ROBUST + IMPLEMENT LOGGING)
        if msg.server == None:
            servname = "(N/A)"
        else:
            servname = msg.server.name
        if type(msg.channel) == discord.PrivateChannel and msg.channel.name == None:
            channame = "(DM) [{}]".format(','.join([str(u) for u in msg.channel.recipients]))
        else:
            channame = msg.channel.name
        if self.user.mentioned_in(msg):
            ansi = colorama.Fore.BLACK+colorama.Back.WHITE
        elif msg.author == self.user:
            ansi = colorama.Fore.CYAN
        else:
            ansi = ""
        print(ansi+"'{}'@'{}', {} | {}: {}".format(servname, channame, msg.timestamp, str(msg.author), msg.clean_content)+colorama.Style.RESET_ALL)
        # INCOMING MESSAGE LOGGING

        # BOT COMMANDS
        if self.user.mentioned_in(msg):
            m = msg.clean_content.replace("@Digbot","").strip()
            cmd = m.lower()
            args = m.split(":")

            if cmd.startswith("hello"):
                await self.send_message(msg.channel, "Hello!")

            # OWNER ONLY BOT COMMANDS
            if msg.author == OWNER:
                if cmd.startswith("die"):
                    await self.logout()

                try:
                    if cmd.startswith("game"):
                        name = args[1]
                        if name == "off":
                            await self.change_presence(game=None)
                        else:
                            await self.change_presence(game=discord.Game(name=args[1]))

                    if cmd.startswith("send"):
                        user_id = args[1]
                        smsg = args[2]
                        await self.send_message(await self.get_user_info(user_id), smsg)
                except IndexError: # invalid arguments
                    pass

                if cmd.startswith("err"):
                    raise Exception
        # BOT COMMANDS

bot = client()
with open("token.txt", "r") as tf:
    token = tf.read()
bot.run(token)