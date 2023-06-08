import logging
import os

from dotenv import load_dotenv
from nextcord.ext import commands

from .counter import VoteCounter
from .graph_cog import GraphicalDataCog

# Load environment variables from ".env"
load_dotenv()

# Set up logging
logger = logging.getLogger("votecounterer")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
fh = logging.FileHandler("votecounterer.log")

ch.setLevel(logging.DEBUG)
fh.setLevel(logging.INFO)

ch_formatter = logging.Formatter("%(levelname)-8s :: %(message)s")
fh_formatter = logging.Formatter(
    "%(name)s / %(asctime)-23s :: %(levelname)-8s :: %(message)s"
)

ch.setFormatter(ch_formatter)
fh.setFormatter(fh_formatter)

logger.addHandler(ch)
logger.addHandler(fh)

bot = commands.Bot()


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")


vote_counter_cog = VoteCounter()
graphical_data_cog = GraphicalDataCog(vote_counter_cog)

bot.add_cog(vote_counter_cog)
bot.add_cog(graphical_data_cog)
bot.run(os.getenv("DISCORD_TOKEN"))
