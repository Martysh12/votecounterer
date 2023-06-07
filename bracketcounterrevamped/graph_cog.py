from graphs import stats_graph, votes_graph, nextcordise

import nextcord
from nextcord.ext import tasks, commands

class GraphicalDataCog(commands.Cog):
    def __init__(self, vote_counter_cog):
        self.vote_counter = vote_counter_cog

    @nextcord.slash_command(description="Send statistics as graphical embed", guild_ids=[835494729554460702])
    async def stats_as_graph(
        self,
        interaction: nextcord.Interaction,
        spoiler: bool = nextcord.SlashOption(description="Spoiler the image", default=True)
    ):
        if self.vote_counter.stats is None:
            await interaction.send("Wait a little for the bot to finish counting bots.")
            return

        await interaction.send(
            file=nextcordise(
                stats_graph(self.vote_counter.stats),
                "stats_graph.png",
                "Statistics graph",
                spoiler
            )
        )
    
    @nextcord.slash_command(description="Send votes as graphical embed", guild_ids=[835494729554460702])
    async def votes_as_graph(
        self,
        interaction: nextcord.Interaction,
        sort: bool = nextcord.SlashOption(description="Sort the bars", default=True),
        spoiler: bool = nextcord.SlashOption(description="Spoiler the image", default=True)
    ):
        if self.vote_counter.stats is None:
            await interaction.send("Wait a little for the bot to finish counting bots.")
            return

        await interaction.send(
            file=nextcordise(
                votes_graph(self.vote_counter.stats, sort=sort),
                "votes_graph.png",
                "Vote graph",
                spoiler
            )
        )
