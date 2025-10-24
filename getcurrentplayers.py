import requests
import csv
import logging
import time
import os
from typing import List, Dict, Optional

# === Configuration ===
API_KEY = "67CEF752436D7BA3046EB48E13E4D13D"  # ← replace with your actual key
PLAYER_COUNT_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
INPUT_CSV = "steam_all_apps.csv"
OUTPUT_CSV = "steam_app_playercounts.csv"
RATE_LIMIT_SECONDS = 1.0  # delay between requests to avoid hitting limits

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# === Function to fetch player count ===
def fetch_current_players(appid: int) -> Optional[int]:
    params = {
        "key": API_KEY,
        "appid": appid
    }
    try:
        resp = requests.get(PLAYER_COUNT_URL, params=params)
    except Exception as e:
        logger.error(f"Request error for appid {appid}: {e}")
        return None
    if resp.status_code != 200:
        logger.warning(f"Non-200 response for appid {appid}: {resp.status_code}")
        return None
    try:
        data = resp.json()
    except ValueError:
        logger.error(f"Invalid JSON for appid {appid}")
        return None
    count = data.get("response", {}).get("player_count")
    return count

# === Main workflow ===
def main(limit: Optional[int] = None):
    # Read input CSV
    logger.info(f"Reading input CSV '{INPUT_CSV}' …")
    apps = []
    with open(INPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit is not None and i >= limit:
                break
            try:
                appid = int(row["appid"])
            except (KeyError, ValueError):
                continue
            name = row.get("name", "")
            apps.append({"appid": appid, "name": name})
    logger.info(f"Loaded {len(apps)} apps from CSV.")

    # Fetch player counts
    results: List[Dict] = []
    for idx, app in enumerate(apps, start=1):
        appid = app["appid"]
        name = app["name"]
        logger.info(f"[{idx}/{len(apps)}] Fetching player count for {name} (appid {appid})")
        count = fetch_current_players(appid)
        results.append({
            "appid": appid,
            "name": name,
            "player_count": count if count is not None else 0
        })
        # Delay
        time.sleep(RATE_LIMIT_SECONDS)

    # Save results to CSV
    logger.info(f"Writing output CSV '{OUTPUT_CSV}' …")
    with open(OUTPUT_CSV, mode="w", newline='', encoding='utf-8') as f:
        fieldnames = ["appid", "name", "player_count"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    logger.info("Done.")

if __name__ == "__main__":
    # You may pass limit=1000 to only fetch first 1000 apps, e.g., main(limit=1000)
    main(limit=100)