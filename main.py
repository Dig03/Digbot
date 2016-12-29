import discord
import asyncio
import traceback
import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
"""
 -- LOGGING TO FILES IS DISABLED FOR NOW --
fh = logging.FileHandler("log_filename.txt")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
"""
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

client = discord.Client()

@client.event
async def on_ready():
    logger.info("Logged in as {}, with ID {}".format(client.user.name, client.user.id))

@client.event
async def on_error(event, *args, **kwargs):
    logging.error(traceback.format_exc())

@client.event
async def on_message(msg):

    # MESSAGE LOGGING
    servname = "(N/A)" if msg.server == None else msg.server.name
    if type(msg.channel) == discord.PrivateChannel and msg.channel.name == None:
        channame = "(DM) [{}]".format(','.join([str(u) for u in msg.channel.recipients]))
    else:
        channame = msg.channel.name
    logging.info("'{}'@'{}', {} | {}: {}".format(servname, channame, msg.timestamp, str(msg.author), msg.clean_content))
    # MESSAGE LOGGING

with open("token", "r") as tf:
    token = tf.read()
client.run(token)