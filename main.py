import discord
import asyncio
import traceback
import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# fh = logging.FileHandler("log_filename.txt")
# fh.setLevel(logging.INFO)
# fh.setFormatter(formatter)
# logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

class CommandSet(object):
    """
    Constructs the configuration of the class.
        parse_cfg - a list of arguments for parse_msg after msg
        client    - the client instance to communicate with the discord api through
    """
    def __init__(self, parse_cfg, client):
        if (len(parse_cfg) != 4) or (type(parse_cfg) is not list) and (type(parse_cfg) is not tuple):
            raise TypeError("parse_cfg must be a list or tuple of length 4")
        #if type(client) is not discord.Client:
        #    raise TypeError("client must be a discord.Client instance")
        #if not client.is_logged_in:
        #    raise ValueError("client must be logged in")
        self.parse_cfg = parse_cfg
        self.client = client
        self.cmds = {}

    async def add(self, cmd_str, ex_argv, func, flat_perms=None, serv_perms=None):
        """
        Registers a command with the CommandSet instance.
            cmd_str - the "cmd" string from parse_msg to trigger this command
            ex_argv - a list of expected arguments with the name of each argument, prefix the argument name with "\v" if it is optional.
                    - optional arguments must terminate the arg list.
            func    - the function to pass parsed_msg (msg ran through parse_msg) to when the command is called
            flat_perms - a list or single (string) user ID which is allowed to use this command
            serv_perms - a list with a server ID at index 0, and another list or single (string) role which is allowed to use this command
            NOTE: flat_perms will take priority over serv_perms, so a flat_perms allowed user who is not serv_perms allowed will be allowed.
        """
        cmd = {}
        if (type(cmd_str) is not str) or (type(ex_argv) is not list):
            raise TypeError("cmd and ex_argv must be convertible to string and list respectively")
        cmd["ex_argv"] = ex_argv
        cmd["ex_argc"] = len(ex_argv)
        if not callable(func) or func.__code__.co_argcount != 1:
            raise TypeError("func must be a function accepting one argument (parsed_msg)")
        cmd["func"] = func
        if flat_perms is not None:
            if (type(flat_perms) is not list) and (type(flat_perms) is not tuple):
                if type(flat_perms) is str:
                    cmd["flat_perms"] = [await self.client.get_user_info(flat_perms)]
                else:
                    raise TypeError("flat_perms must be list, tuple or str")
            else:
                cmd["flat_perms"] = []
                async for s in flat_perms:
                    cmd["flat_perms"].append(await self.client.get_user_info(s))
        else:
            cmd["flat_perms"] = None 
        if serv_perms is not None:
            if (len(serv_perms) != 2) or (type(serv_perms[0]) is not str) or (type(serv_perms[1]) is not list) and (type(serv_perms[1]) is not tuple):
                if type(serv_perms[1]) is str:
                    cmd["serv_perms"] = []
                    cmd["serv_perms"][0] = self.client.get_server(serv_perms[0])
                    cmd["serv_perms"][1] = [r for r in cmd["serv_perms"][0].roles if str(r) == serv_perms[1]]
                else:
                    raise TypeError("serv_perms must be a length 2 list, with a string at index 0, and a list, tuple or string at index 1")
            else:
                cmd["serv_perms"] = []
                cmd["serv_perms"][0] = self.client.get_server(serv_perms[0])
                cmd["serv_perms"][1] = []
                for role in serv_perms[1]:
                    for r in cmd["serv_perms"][0].roles:
                        if str(r) == role:
                            cmd["serv_perms"][1].append(r)
        else:
            cmd["serv_perms"] = None
        self.cmds[cmd_str] = cmd

    def parse_msg(self, msg, trig_str, trig_delim, cmd_delim, arg_delim):
        """
        Parses msg according to [trig_str][trig_delim]<command>[cmd_delim]<arg>[arg_delim]<arg>
            if trig_str is at the start of the msg:
                if no command present, returns False
                if command present: 
                    returns dictionary with:
                        <command> @ key 'cmd',
                        None @ key 'argv',
                        0 @ key 'argc'
                if command present with some arguments:
                    returns dictionary with:
                        <command> @ key 'cmd',
                        [<arg>, <arg>] @ key 'argv',
                        len('argv') @ key 'argc'
            else:
                returns False

            NOTE: prepending arg_delim with '\' will escape splitting at that position.
        """
        if ((trig_delim is None) or (' ' in trig_delim)) and ' ' in trig_str:
            raise ValueError("trig_str cannot have whitespace when splitting by whitespace.")
        if trig_delim is not None and trig_delim in trig_str:
            raise ValueError("trig_delim cannot be within trig_str. Impossible to parse.")
        delim = [trig_delim, cmd_delim, arg_delim]
        if len(delim) != len(set(delim)):
            raise ValueError("delimiters cannot equal each other. Impossible to parse.")
        msg = msg.strip()
        msg = msg.split(trig_delim, 1)
        if msg[0] == trig_str:
            if len(msg) == 2:
                if cmd_delim in msg[1]:
                    msg[1]    = msg[1].split(cmd_delim, 1)
                    msg[1][1] = re.split(r"(?<!\\)"+arg_delim, msg[1][1])
                    msg[1][1] = [s.replace("\\,", ",") for s in msg[1][1]]
                    return {'cmd': msg[1][0], 'argv': msg[1][1], 'argc': len(msg[1][1])}
                else:
                    return {'cmd': msg[1], 'argv': None, 'argc': 0}
            else:
                return False
        else:
            return False

class Client(discord.Client):

    async def on_ready(self): 
        self.OWNER = await self.get_user_info("196391063987027969")
        logger.info("Logged in as "+self.user.name+", with ID "+self.user.id)

    async def phone_home(self, msg):
        await self.send_message(self.OWNER, msg)

    async def on_error(self, event, *args, **kwargs):
        err = traceback.format_exc()
        logging.error("An error was encountered during execution")
        logging.error(err)
        await self.phone_home("```Python\n"+err+"```")

    async def on_message(self, msg):

        # COMMAND SYSTEM
        """
        Command syntax:
            [trig_str][trig_delim]<command>[cmd_delim]<arg>[arg_delim]<arg>
        """
        parse_cfg = ("~db", None, ":", ",") # CREATE COMMANDSET INSTANCE HERE

        # COMMAND SYSTEM

        # MESSAGE LOGGING
        serv = "(N/A)" if msg.server == None else msg.server.name
        if type(msg.channel) == discord.PrivateChannel and msg.channel.name == None:
            channame = "(DM) [{}]".format(','.join([str(u) for u in msg.channel.recipients]))
        else:
            channame = msg.channel.name
        logging.info("'{}'@'{}', {} | {}: {}".format(servname, channame, msg.timestamp, str(msg.author), msg.clean_content))
        # MESSAGE LOGGING
"""
bot = Client()
with open("token", "r") as tf:
    token = tf.read()
bot.run(token)
"""