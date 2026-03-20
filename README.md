# SFGArchived

Telegram bot that posts a link to the full archived game broadcast on MLB.tv for the most recent SF Giants game.

Companion to [SFGCondensed](../SFGCondensed), which posts the condensed game MP4. This one links to the full broadcast instead.

## What it does

1. Queries the MLB Stats API for Giants games in the last 7 days
2. Finds the most recent one with a `Final` status that hasn't been posted yet
3. Posts the MLB.tv archive link to the Telegram channel
4. Logs the game PK locally so it doesn't double-post

## Automated runs

A GitHub Actions workflow (`.github/workflows/daily.yml`) runs the bot every day at **10:00 UTC (3:00 AM PT)** — safely after any West Coast evening game.

After each run, the workflow commits the updated `posted_archived.txt` state file back to the repo so duplicate detection works across runs.

### Triggering manually

Go to **Actions → Daily Archive Post → Run workflow**. An optional `force_post` input is available to skip the duplicate check and re-post the most recent game.

### Secrets required

Add these in **Settings → Secrets → Actions**:

| Secret | Description |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot API token from @BotFather |
| `TELEGRAM_CHAT_ID` | Target chat/channel ID |

`FORCE_POST` is not a secret — pass it as the `force_post` workflow input instead.

## Running locally

```bash
pip install -r requirements.txt
python run_bot.py
```

Or double-click `run_bot.bat`. Requires a `.env` file with `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (see `.env.example` or the secrets table above).

## State tracking

Posted game PKs are written to `posted_archived.txt` in this directory. In Actions, this file is committed back to the repo after each run. Locally, delete it to reset.

## Known limitations

- The `mlb.com/tv/g{gamePk}` URL requires an MLB.tv subscription to watch
