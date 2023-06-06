import requests

import nextcord
from nextcord.ext import tasks, commands

from dataclasses import dataclass
import logging
import os

logger = logging.getLogger('votecounterer')

class VoteCountingException(BaseException):
    pass

class VoteCounter(commands.Cog):
    def __init__(self):
        self.stats = None
        self.valid_letters = ['a', 'b', 'c', 'd', 'e']

        logger.info("VoteCounter cog initialised.")

        self.count_votes.start()

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
            'unique_voters': 0,
            'duplicate_comments': 0,
            'duplicate_commenters': 0,
            'most_prolific_duplicator': "",
            'most_prolific_duplicator_votes': 0,
            'votes': {
                letter: 0
                for letter in self.valid_letters
            }
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
            is_vote = False
            for letter in self.valid_letters:
                if f"[{letter}]" in comment_content.lower():
                    vote_stats['vote_comments'] += 1
                    vote_stats['votes'][letter] += 1
                    is_vote = True
                    break

            if not is_vote:
                vote_stats['non_vote_comments'] += 1
                continue # Nothing to see here

            # Duplicator-catching mechanism

            # Has channel voted before?
            #   Yes: Is channel in the duplicators list?
            #       Yes: Increase vote count by one.
            #       No: Create an entry with a vote count of 2.
            #   No: Add channel to the people who voted list.

            if channel_id in people_who_voted:
                vote_stats['duplicate_comments'] += 1

                if channel_id in duplicators:
                    duplicators[channel_id]['votes'] += 1
                else:
                    duplicators[channel_id] = {'name': channel_name, 'votes': 2}
            else:
                people_who_voted.append(channel_id)

        # Count the duplicators (and the voters)
        vote_stats['unique_voters'] = len(people_who_voted)
        vote_stats['duplicate_commenters'] = len(duplicators)
        vote_stats['duplicate_comments'] = 0

        for channel_id, data in duplicators.items():
            vote_stats['duplicate_comments'] += data['votes']

            if data['votes'] > vote_stats['most_prolific_duplicator_votes']:
                vote_stats['most_prolific_duplicator'] = data['name']
                vote_stats['most_prolific_duplicator_votes'] = data['votes']

        logger.debug(vote_stats)

        # Finally, replace the older stats
        self.stats = vote_stats
