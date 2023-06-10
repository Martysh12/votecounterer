import logging
import os
from datetime import datetime, timezone

import nextcord
import requests
from nextcord.ext import commands, tasks

from .embeds import TextualStatsEmbed, TextualVotesEmbed

logger = logging.getLogger("votecounterer")


class VoteCountingException(Exception):
    pass


class VoteCounter(commands.Cog):
    def __init__(self):
        self.stats = None
        self.valid_letters = [
            "a",
            "b",
            "c",
            "d",
            "e",
        ]  # TODO: Un-hardcode the letters
        self.video_published_at = datetime.fromisoformat(
            "2023-06-06T17:00:32Z"
        )

        logger.info("VoteCounter cog initialised.")

        self.count_votes.add_exception_type(
            VoteCountingException, ConnectionError
        )
        self.count_votes.start()  # pylint: disable=no-member

    @nextcord.slash_command(description="Send statistics as textual embed")
    async def stats_as_text(self, interaction: nextcord.Interaction):
        if self.stats is None:
            await interaction.send(
                "Wait a little for the bot to finish counting votes."
            )
            return

        await interaction.send(embed=TextualStatsEmbed(self.stats))

    @nextcord.slash_command(description="Send votes as textual embed")
    async def votes_as_text(self, interaction: nextcord.Interaction):
        if self.stats is None:
            await interaction.send(
                "Wait a little for the bot to finish counting votes."
            )
            return

        await interaction.send(embed=TextualVotesEmbed(self.stats))

    @tasks.loop(minutes=45.0)
    async def count_votes(self):
        logger.debug("Downloading comments...")

        params = {
            "key": os.getenv("YOUTUBE_API_KEY"),
            "part": "snippet",
            "videoId": "jWZ6p_JeLyc",  # TODO: Un-hardcode the video ID
            "textFormat": "plainText",
            "maxResults": 100,
            "moderationStatus": "published",
            "order": "orderUnspecified",
        }

        comments = []

        session = requests.Session()

        while True:
            data = session.get(
                "https://youtube.googleapis.com/youtube/v3/commentThreads",
                params=params,
            ).json()

            if "error" in data:
                logger.error(data["error"]["message"])
                raise VoteCountingException(data["error"]["message"])

            comments += data["items"]

            # Have we downloaded everything?
            if "nextPageToken" not in data:
                break

            next_page_token = data["nextPageToken"]
            params["pageToken"] = next_page_token

        # Let the counting start
        logger.debug("Counting votes...")

        vote_stats = {
            "total_comments": 0,
            "vote_comments": 0,
            "non_vote_comments": 0,
            "duplicate_comments": 0,
            "duplicate_commenters": 0,
            "most_prolific_duplicator": "",
            "most_prolific_duplicator_votes": 0,
            "late_votes": 0,
            "votes": {letter: 0 for letter in self.valid_letters},
            "counted_at": datetime.now(timezone.utc),
        }

        people_who_voted = []  # list of [channel_id, ...]
        duplicators = {}  # dict of {channel_id: {'name':, 'votes':}}
        for comment in comments:
            # Thanks YouTube
            actual_comment = comment["snippet"]["topLevelComment"]["snippet"]

            if "authorChannelId" not in actual_comment:
                # Sometimes there's just no channel ID? Weird.
                continue

            channel_name = actual_comment["authorDisplayName"]
            channel_id = actual_comment["authorChannelId"]["value"]
            comment_content = actual_comment["textOriginal"]

            vote_stats["total_comments"] += 1

            # Check if comment is a vote
            is_vote = False
            for letter in self.valid_letters:
                if f"[{letter}]" in comment_content.lower():
                    is_vote = True
                    break

            if not is_vote:
                vote_stats["non_vote_comments"] += 1
                continue  # Nothing to see here

            # From now on, the comment is 100% a vote

            # Check if vote is late
            comment_published_at = datetime.fromisoformat(
                actual_comment["publishedAt"]
            )
            how_late = comment_published_at - self.video_published_at

            if how_late.days >= 2:
                vote_stats["late_votes"] += 1
                continue  # Vote is late, therefore it's invalid

            if channel_id in people_who_voted:
                vote_stats["duplicate_comments"] += 1

                if channel_id in duplicators:
                    duplicators[channel_id]["votes"] += 1
                else:
                    # 'votes' should count the number of duplicate votes,
                    # not the total amount of votes that person has cast
                    duplicators[channel_id] = {
                        "name": channel_name,
                        "votes": 1,
                    }
            else:
                people_who_voted.append(channel_id)

                vote_stats["vote_comments"] += 1
                vote_stats["votes"][letter] += 1

        # Count the duplicators
        vote_stats["duplicate_commenters"] = len(duplicators)

        for channel_id, data in duplicators.items():
            if data["votes"] > vote_stats["most_prolific_duplicator_votes"]:
                vote_stats["most_prolific_duplicator"] = data["name"]
                vote_stats["most_prolific_duplicator_votes"] = data["votes"]

        logger.debug(vote_stats)

        # Finally, replace the older stats
        self.stats = vote_stats
