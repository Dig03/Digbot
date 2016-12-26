import discord
import asyncio
import traceback
import colorama
import random
import logging

colorama.init()

class client(discord.Client):

    async def on_ready(self):
        global OWNER 
        OWNER = await self.get_user_info("196391063987027969")
        self.trigger_string = "~digbot"
        print("READY")

    async def phone_home(self, msg):
        await self.send_message(OWNER, msg)

    async def on_error(self, event, *args, **kwargs):
        err = traceback.format_exc()
        print(colorama.Fore.RED+err+colorama.Fore.RESET)
        await self.phone_home("```Python\n"+err+"```")

    async def on_message(self, msg):

        # COMMAND SYSTEM
        """
            FOR NOTE:
                COMMAND SYNTAX IS AS FOLLOWS,
                ~digbot <command>:<argument>,<argument>...
        """
        parsed_msg = msg.clean_content.split(":")
        parsed_msg[0] = parsed_msg[0].lower()
        parsed_msg[0] = parsed_msg[0].split()
        if len(parsed_msg[0]) > 1:
            cmd = ' '.join(parsed_msg[0][1:])
            msg_trig = True
        else:
            msg_trig = False

        if len(parsed_msg) > 1:
            args = parsed_msg[1].split(",")
        else:
            args = False

        if msg_trig:

            chan = msg.channel

            if cmd == "hello":
                await self.send_message(chan, random.choice(["Hello!", "Salutation!", "Hi there!", "Hi.", "Hello.", "Hey!"]))

            if args: # commands requiring arguments
                if cmd == "echo":
                    await self.send_message(chan, ','.join(args[0:]))

            if msg.author == OWNER:
                if cmd == "die":
                    await self.logout()

                if args:
                    if cmd == "game":
                        name = args[0]
                        if name == "off":
                            await self.change_presence(game=None)
                        else:
                            await self.change_presence(game=discord.Game(name=name))

                    if cmd == "send":
                        user_id = args[0]
                        smsg = ",".join(args[1:])
                        await self.send_message(await self.get_user_info(user_id), smsg)

        # COMMAND SYSTEM

        # INCOMING MESSAGE LOGGING (TODO: MAKE THIS MORE ROBUST + IMPLEMENT LOGGING)
        # TODO: DURING EXCEPTIONS LOGGING DOES NOT FUNCTION CORRECTLY, LOGGING SHOULD BE MOVED TO A FUNCTION AND CALLED HERE, AND IN ON_ERROR TO ALLEVIATE THIS.
        if msg.server == None:
            servname = "(N/A)"
        else:
            servname = msg.server.name
        if type(msg.channel) == discord.PrivateChannel and msg.channel.name == None:
            channame = "(DM) [{}]".format(','.join([str(u) for u in msg.channel.recipients]))
        else:
            channame = msg.channel.name
        if msg_trig:
            ansi = colorama.Fore.BLACK+colorama.Back.WHITE
            msg_trig = False
        elif msg.author == self.user:
            ansi = colorama.Fore.CYAN
        else:
            ansi = ""
        print(ansi+"'{}'@'{}', {} | {}: {}".format(servname, channame, msg.timestamp, str(msg.author), msg.clean_content)+colorama.Style.RESET_ALL)
        # INCOMING MESSAGE LOGGING


bot = client()
with open("token", "r") as tf:
    token = tf.read()
bot.run(token)