from embeds import TextualStatsEmbed, TextualVotesEmbed

import requests

import nextcord
from nextcord.ext import tasks, commands

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import os

logger = logging.getLogger('votecounterer')

class VoteCountingException(BaseException):
    pass

class VoteCounter(commands.Cog):
    def __init__(self):
        self.stats = None
        self.valid_letters = ['a', 'b', 'c', 'd', 'e'] # TODO: Un-hardcode the letters

        logger.info("VoteCounter cog initialised.")

        self.count_votes.start()

    @nextcord.slash_command(description="Send statistics as textual embed", guild_ids=[835494729554460702])
    async def stats_as_text(self, interaction: nextcord.Interaction):
        if self.stats is None:
            await interaction.send("Wait a little for the bot to finish counting votes.")
            return

        await interaction.send(embed=TextualStatsEmbed(self.stats))
    
    @nextcord.slash_command(description="Send votes as textual embed", guild_ids=[835494729554460702])
    async def votes_as_text(self, interaction: nextcord.Interaction):
        if self.stats is None:
            await interaction.send("Wait a little for the bot to finish counting votes.")
            return

        await interaction.send(embed=TextualVotesEmbed(self.stats))

    @tasks.loop(minutes=45.0)
    async def count_votes(self):
        logger.debug(f"Downloading comments...")

        params = {
            'key': os.getenv('YOUTUBE_API_KEY'),
            'part': 'snippet',
            'videoId': 'jWZ6p_JeLyc', # TODO: Un-hardcode the video ID
            'textFormat': 'plainText',
            'maxResults': 100,
            'moderationStatus': 'published',
            'order': 'orderUnspecified'
        }

        comments = []

        s = requests.Session()

        while True:
            data = s.get('https://youtube.googleapis.com/youtube/v3/commentThreads', params=params).json()

            if 'error' in data:
                raise VoteCountingException(data["message"])

            comments += data['items']

            # Have we downloaded everything?
            if 'nextPageToken' not in data:
                break

            next_page_token = data['nextPageToken']
            params['pageToken'] = next_page_token

        # Let the counting start
        logger.debug(f"Counting votes...")

        vote_stats = {
            'total_comments': 0,
            'vote_comments': 0,
            'non_vote_comments': 0,
            'duplicate_comments': 0,
            'duplicate_commenters': 0,
            'most_prolific_duplicator': "",
            'most_prolific_duplicator_votes': 0,
            'votes': {
                letter: 0
                for letter in self.valid_letters
            },
            'counted_at': datetime.now(timezone.utc)
        }

        people_who_voted = [] # list of [channel_id, ...]
        duplicators = {} # dict of {channel_id: {'name':, 'votes':}}
        for comment in comments:
            # Thanks YouTube
            actual_comment = comment['snippet']['topLevelComment']['snippet']

            channel_name = actual_comment['authorDisplayName']
            channel_id = actual_comment['authorChannelId']['value']
            comment_content = actual_comment['textOriginal']

            vote_stats['total_comments'] += 1

            # Check if comment is a vote
            voted_for = None
            is_vote = False
            for letter in self.valid_letters:
                if f"[{letter}]" in comment_content.lower():
                    voted_for = letter
                    is_vote = True
                    break

            if not is_vote:
                vote_stats['non_vote_comments'] += 1
                continue # Nothing to see here

            if channel_id in people_who_voted:
                vote_stats['duplicate_comments'] += 1
                
                if channel_id in duplicators:
                    duplicators[channel_id]['votes'] += 1
                else:
                    duplicators[channel_id] = {
                        'name': channel_name,
                        'votes': 1 # This counts the number of duplicate votes, not the total amount of votes that person has cast
                    }
            else:
                people_who_voted.append(channel_id)

                vote_stats['vote_comments'] += 1
                vote_stats['votes'][letter] += 1

        # Count the duplicators
        vote_stats['duplicate_commenters'] = len(duplicators)

        for channel_id, data in duplicators.items():
            if data['votes'] > vote_stats['most_prolific_duplicator_votes']:
                vote_stats['most_prolific_duplicator'] = data['name']
                vote_stats['most_prolific_duplicator_votes'] = data['votes']

        logger.debug(vote_stats)

        # Finally, replace the older stats
        self.stats = vote_stats
