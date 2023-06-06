from dotenv import load_dotenv

import nextcord
from nextcord.ext import commands

import logging
import os

# Load environment variables from ".env"
load_dotenv()

# Set up logging
logger = logging.getLogger('votecounterer')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
fh = logging.FileHandler('votecounterer.log')

ch.setLevel(logging.DEBUG)
fh.setLevel(logging.INFO)

ch_formatter = logging.Formatter('%(levelname)-8s :: %(message)s')
fh_formatter = logging.Formatter('%(name)s / %(asctime)-23s :: %(levelname)-8s :: %(message)s')

ch.setFormatter(ch_formatter)
fh.setFormatter(fh_formatter)

logger.addHandler(ch)
logger.addHandler(fh)

TESTING_GUILD_ID = 835494729554460702

bot = commands.Bot()

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

bot.run(os.getenv('DISCORD_TOKEN'))
