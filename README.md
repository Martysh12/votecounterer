# votecounterer
A Discord bot for counting votes for the OSO Discord server.

## Commands
### Stats
`/stats_as_graph` - Display stats as a pretty graph  
`/stats_as_text` - Display stats as a Discord embed

### Votes
`/votes_as_graph` - Display votes as a pretty graph  
`/votes_as_text` - Display stats as a Discord embed

## Running
1. Create a `.env` file with the following syntax:
```
DISCORD_TOKEN={your Discord bot token}
YOUTUBE_API_KEY={your YouTube API key}
```
2. That's it! Launch the bot with `poetry run python -m votecounterer`

## Contributing
1. Fork the repository
2. Create a branch for your feature/fix on the fork
3. Install [Poetry](https://python-poetry.org/).
4. Run `poetry install` in the repository to install all dependencies.
5. Run `poetry run task pre-commit` to install the pre-commit hook.
    - It will lint your code to fit this repository's standards
    - It will tell you what's wrong with your code
6. Write your fixes! You will see that committing will take an unusually long amount of time, because the hooks you just installed are checking the code.
7. Upload the branch (if you haven't already) and create a pull-request here.
