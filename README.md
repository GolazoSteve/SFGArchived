# SFGArchived

Telegram bot that posts a link to the full archived game broadcast on MLB.tv for the most recent SF Giants game.

Companion to [SFGCondensed](../SFGCondensed), which posts the condensed game MP4. This one links to the full broadcast instead.

## What it does

1. Queries the MLB Stats API for Giants games in the last 7 days
2. Finds the most recent one with a `Final` status that hasn't been posted yet
3. Posts a Telegram message with a **Watch** button
4. The button opens a GitHub Pages landing page (`/watch/`) which deep-links directly into the MLB app (`mlbatbat://mlbtv?gamepk=...&date=...`) — bypassing the browser entirely on Android
5. Logs the game PK so it doesn't double-post

## How the deep link works

Telegram inline keyboard buttons can only use `http`/`https` URLs, so the button points to a GitHub Pages landing page rather than the `mlbatbat://` scheme directly. That page offers two options:

- **Open in MLB App** — fires `mlbatbat://mlbtv?gamepk={gamePk}&date={YYYYMMDD}`, opening the archived broadcast straight in the app
- **Open in Browser** — falls back to `mlb.com/tv/g{gamePk}` for desktop or non-app users

The landing page picks a random line from `watch/copy.json` on each load and credits the whole operation to Steve Klein, with a PayPal tip link.

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

Or double-click `run_bot.bat`. Requires a `.env` file with `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

## State tracking

Posted game PKs are written to `posted_archived.txt`. In Actions, this file is committed back to the repo after each run. Locally, delete it to reset.

## Known limitations

- Watching requires an MLB.tv subscription
- The `mlbatbat://` deep link scheme is undocumented — discovered by inspecting MLB's Next.js JS bundle. May break if MLB changes their app's URL routing
- Spring Training games appear in the schedule API but may not have archived broadcasts available
