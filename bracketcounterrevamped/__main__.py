from dotenv import load_dotenv

import nextcord
from nextcord.ext import commands

import os

load_dotenv()

TESTING_GUILD_ID = 835494729554460702

bot = commands.Bot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(description="My first slash command", guild_ids=[TESTING_GUILD_ID])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")

bot.run(os.getenv("DISCORD_TOKEN"))
