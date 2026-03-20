import requests
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from dateutil.parser import parse

load_dotenv()

REQUIRED_ENV_VARS = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
if missing:
    print(f"❌ Missing required env vars: {', '.join(missing)}")
    exit(1)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
POSTED_GAMES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posted_archived.txt")
TEAM_ID = int(os.getenv("TEAM_ID", "137"))
FORCE_POST = os.getenv("FORCE_POST", "false").lower() == "true"


def fetch_with_retry(url, retries=3, backoff=2, **kwargs):
    for attempt in range(retries):
        try:
            res = requests.get(url, **kwargs)
            if res.status_code == 200:
                return res
            print(f"⚠️ HTTP {res.status_code} for {url} (attempt {attempt + 1})")
        except Exception as e:
            print(f"⚠️ Request error: {e} (attempt {attempt + 1})")
        if attempt < retries - 1:
            time.sleep(backoff)
    return None


def get_recent_gamepks(team_id=137):
    now_uk = datetime.now(ZoneInfo("Europe/London"))
    start_date = (now_uk - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = (now_uk + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate={start_date}&endDate={end_date}"
    res = fetch_with_retry(url, timeout=10)
    if res is None:
        print("❌ Could not fetch MLB schedule")
        return []
    data = res.json()
    games = []
    for date in data["dates"]:
        for game in date["games"]:
            if game["status"]["detailedState"] in ("Final", "Completed Early"):
                game_pk = game["gamePk"]
                game_date = game["gameDate"]
                away = game["teams"]["away"]["team"]["name"]
                home = game["teams"]["home"]["team"]["name"]
                games.append((parse(game_date), game_pk, away, home))
    games.sort(reverse=True)
    return [(pk, away, home) for _, pk, away, home in games]


def already_posted(gamepk):
    if not os.path.exists(POSTED_GAMES_FILE):
        return False
    with open(POSTED_GAMES_FILE, "r") as f:
        return str(gamepk) in f.read().splitlines()


def mark_as_posted(gamepk):
    with open(POSTED_GAMES_FILE, "a") as f:
        f.write(f"{gamepk}\n")


def send_telegram_message(gamepk, away, home):
    web_url = f"https://www.mlb.com/tv/g{gamepk}"
    message = f"📺 {away} @ {home}"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "Watch", "url": web_url},
                ]
            ]
        },
    }
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload,
            timeout=10,
        )
        return res.ok
    except Exception as e:
        print(f"❌ Telegram send failed: {e}")
        return False


def main():
    print("📺 Archived Game Bot")
    if FORCE_POST:
        print("⚡ FORCE_POST mode enabled — skipping already-posted check")

    games = get_recent_gamepks(team_id=TEAM_ID)
    print(f"🧾 Found {len(games)} recent final games")

    for gamepk, away, home in games:
        print(f"🔍 Checking gamePk: {gamepk} ({away} @ {home})")
        if not FORCE_POST and already_posted(gamepk):
            print("⏩ Already posted")
            continue

        if send_telegram_message(gamepk, away, home):
            mark_as_posted(gamepk)
            print(f"✅ Posted archive link for {gamepk}")
        else:
            print(f"⚠️ Failed to post for {gamepk}")
        break


if __name__ == "__main__":
    main()
