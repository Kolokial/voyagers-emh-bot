# voyagers-emh-bot

A Reddit bot that replies to mentions of Star Trek: Voyager's Emergency Medical Hologram with a quote from the show.

## What it does

- **`src/startConversation.py`** reads the 50 hottest posts in each configured subreddit. It replies once per post to a comment that mentions "the Doctor", "the EMH" or "Voyager's EMH".
- **`src/startLookingForMoreQuotes.py`** checks replies to the bot's comments from the last 30 days and answers anyone asking for "more quotes".

Both run every 12 hours from `.github/workflows/StartVoyagersEMH.yml`.

## Commands people can use

- Reply `optout` (or `ignore me`) as the whole comment: the bot never replies to you again.
- A subreddit moderator replies `gtfo voyagersemh`: the bot stops posting in that subreddit.

## Setup

Set these environment variables (or put them in a `.env` file):

| Variable | Purpose |
| --- | --- |
| `MONGODB_CONNECTION_STRING` | MongoDB Atlas connection string |
| `CLIENT_ID`, `CLIENT_SECRET` | Reddit app credentials |
| `REDDIT_PASSWORD` | Password for u/VoyagersEMH |
| `LOGLEVEL` | Optional, defaults to `INFO` |

The `voyagersEMHBot` database needs a `subreddits` collection with one `{"name": "<subreddit>"}` document per subreddit.

Quotes live in `data/emh-quotes.json`.

## Development

```sh
pip install -r requirements-dev.txt
python -m pytest
```
