import nextcord

DATETIME_FORMAT = "%b %d, %Y / %X %Z"

class TextualStatsEmbed(nextcord.Embed):
    def __init__(self, stats):
        super().__init__(
            colour=nextcord.Colour.gold(),
            title="Textual Stats"
        )

        self.add_field(name="Total comments", value=str(stats['total_comments']), inline=True)
        self.add_field(name="Vote comments", value=str(stats['vote_comments']), inline=True)
        self.add_field(name="Non-vote comments", value=str(stats['non_vote_comments']), inline=True)
        self.add_field(name="Duplicate votes", value=str(stats['duplicate_comments']), inline=False)
        self.add_field(name="Duplicate voters", value=str(stats['duplicate_commenters']), inline=True)
        self.add_field(
            name="Most prolific duplicator",
            value=f"`{stats['most_prolific_duplicator']}`, with an astounding {stats['most_prolific_duplicator_votes']} vote(s)",
            inline=False
        )

        self.set_footer(text=f"Votes last counted at: {stats['counted_at'].strftime(DATETIME_FORMAT)}")

class TextualVotesEmbed(nextcord.Embed):
    def __init__(self, stats):
        super().__init__(
            colour=nextcord.Colour.gold(),
            title="Textual Votes"
        )

        votes = stats['votes']

        percentages = {
            letter: (float(votes) / stats['vote_comments']) * 100
            for letter, votes in votes.items()
        }

        for letter, votes in votes.items():
            self.add_field(name=f"`[{letter}]`", value=f"{votes} ({percentages[letter]:.2f}%)", inline=True)

        self.set_footer(text=f"Votes last counted at: {stats['counted_at'].strftime(DATETIME_FORMAT)}")
