import nextcord
from nextcord.ext import commands

from .graphs import nextcordise, stats_graph, votes_graph


class GraphicalDataCog(commands.Cog):
    def __init__(self, vote_counter_cog):
        self.vote_counter = vote_counter_cog

    @nextcord.slash_command(description="Send statistics as graphical embed")
    async def stats_as_graph(
        self,
        interaction: nextcord.Interaction,
    ):
        if self.vote_counter.stats is None:
            await interaction.send(
                "Wait a little for the bot to finish counting bots."
            )
            return

        await interaction.send(
            file=nextcordise(
                stats_graph(self.vote_counter.stats),
                "stats_graph.png",
                "Statistics graph",
                spoiler=True,
            )
        )

    @nextcord.slash_command(description="Send votes as graphical embed")
    async def votes_as_graph(
        self,
        interaction: nextcord.Interaction,
        sort: bool = nextcord.SlashOption(
            description="Sort the bars", default=True
        ),
    ):
        if self.vote_counter.stats is None:
            await interaction.send(
                "Wait a little for the bot to finish counting bots."
            )
            return

        await interaction.send(
            file=nextcordise(
                votes_graph(self.vote_counter.stats, sort=sort),
                "votes_graph.png",
                "Vote graph",
                spoiler=True,
            )
        )
