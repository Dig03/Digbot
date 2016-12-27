import discord
import asyncio
import traceback
import colorama
import re
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

    def parse_msg(self, msg, trig_str, trig_delim, cmd_delim, arg_delim):
        """
        Parses msg according to [trig_str][trig_delim]<command>[cmd_delim]<arg>[arg_delim]<arg>
            if trig_str is at the start of the msg:
                if no command present, returns False
                if command present: 
                    returns dictionary with:
                        <command> @ key 'cmd',
                        None @ key 'argv',
                        0 at key 'argc'
                if command present with some arguments:
                    returns dictionary with:
                        <command> @ key 'cmd',
                        [<arg>, <arg>] @ key 'argv',
                        len('argv') @ key 'argc'
            else:
                returns False

            NOTE: prepending arg_delim with '\' will escape splitting at that position.
        """
        if ((trig_delim == None) or (' ' in trig_delim)) and ' ' in trig_str:
            raise ValueError("trig_str cannot have whitespace when splitting by whitespace.")
        if trig_delim != None and trig_delim in trig_str:
            raise ValueError("trig_delim cannot be within trig_str. Impossible to parse.")
        msg = msg.strip()
        msg = msg.split(trig_delim, 1)
        if msg[0] == trig_str:
            if len(msg) == 2:
                if cmd_delim in msg[1]:
                    msg[1] = msg[1].split(cmd_delim, 1)
                    msg[1][1] = re.split(r"(?<!\\)"+arg_delim,msg[1][1])
                    msg[1][1] = [s.replace("\\,", ",") for s in msg[1][1]]
                    return {'cmd': msg[1][0], 'argv': msg[1][1], 'argc': len(msg[1][1])}
                else:
                    return {'cmd': msg[1], 'argv': None, 'argc': 0}
            else:
                return False
        else:
            return False

    async def on_message(self, msg):

        # COMMAND SYSTEM
        """
        Command syntax:
            [trig_str][trig_delim]<command>[cmd_delim]<arg>[arg_delim]<arg>
        """
        parsed_msg = self.parse_msg(msg.clean_content, "~db", None, ":", ",")
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
        print("'{}'@'{}', {} | {}: {}".format(servname, channame, msg.timestamp, str(msg.author), msg.clean_content))
        # INCOMING MESSAGE LOGGING

"""
bot = client()
with open("token", "r") as tf:
    token = tf.read()
bot.run(token)
"""