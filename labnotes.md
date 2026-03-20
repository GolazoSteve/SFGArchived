# SFGArchived Lab Notes

## Session: 2026-03-20 — Initial Build

### What this bot does
Checks the MLB Stats API for the most recent SF Giants game with a Final status, then posts the full archived game broadcast link on MLB.tv to a Telegram channel. Runs manually via `run_bot.bat`.

---

### How it was built
Started from the SFGCondensed bot as a reference. Key differences:
- No Google Drive — state tracked locally in `posted_archived.txt`
- No email — Telegram only
- No condensed game lookup — just constructs the MLB.tv URL from the gamePk
- No copy/quip — just a plain link for now

---

### Key Finding: MLB API doesn't expose full game archive URLs
Investigated the `statsapi.mlb.com/api/v1/game/{gamePk}/content` endpoint thoroughly. It returns:
- Condensed game MP4 (via `mlb-cuts-diamond.mlb.com`)
- Individual highlight clips
- Editorial recap (links to `dapi.mlbinfra.com`, not a watchable URL)

There is no full game archive URL in the public API. Full game replays are auth-gated on MLB.tv. The correct URL to link to the MLB.tv player for an archived game is:

```
https://www.mlb.com/tv/g{gamePk}
```

Tested and confirmed this loads the MLB.tv player shell. If the user is already logged in, it plays the archived broadcast.

### URL formats that don't work
- `https://www.mlb.com/live-stream-games/{gamePk}/` — 404
- `https://www.mlb.com/gameday/{gamePk}/final/game-recap` — 404
- `https://www.mlb.com/video/archive-game/{gamePk}` — 404

---

### Google Drive dropped
Initially copied the Drive upload/download pattern from SFGCondensed. Hit a 404 error when trying to CREATE a new file in the Drive folder — the service account can update existing files but fails to create new ones (likely a shared drive permissions issue). Since this bot runs locally (not from stateless GitHub Actions), Drive isn't needed. Switched to local file tracking only.

---

### Outstanding / Future Ideas

- **Mobile deep-link**: ~~`mlb.com/tv/g{gamePk}` on mobile prompts to download the MLB app rather than opening in-app.~~ **Resolved (2026-03-20)**: The root cause was Telegram's internal WebView stripping iOS Universal Link / Android App Link context when a URL appears in message text. Fix: moved links out of the message body and into a Telegram inline keyboard (`reply_markup`). The OS then handles the URL natively, enabling app handoff. Added two buttons — "Watch in App" (`mlbatbat://watch?contentId={gamePk}&type=game`, the MLB app's registered URI scheme) and "Watch on Web" (`https://www.mlb.com/tv/g{gamePk}`). Also switched the API call from `data=` to `json=` to support the nested `reply_markup` dict.
- **GitHub Actions workflow**: not set up yet — currently manual only
- **Add a quip/copy line**: intentionally deferred for now
- **Scheduled runs**: could run on the same 5-min cron as SFGCondensed once a workflow is added
