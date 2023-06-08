# votecounterer
A Discord bot for counting votes for the OSO Discord server.

## Commands
### Stats
`/stats_as_graph` - Display stats as a pretty graph  
`/stats_as_text` - Display stats as a Discord embed

## Votes
`/votes_as_graph` - Display votes as a pretty graph  
`/votes_as_text` - Display stats as a Discord embed

## Running
1. Create a `.env` file with the following syntax:
```
DISCORD_TOKEN={your Discord bot token}
YOUTUBE_API_KEY={your YouTube API key}
```
2. That's it! Launch the bot with `poetry run python -m votecounterer`
