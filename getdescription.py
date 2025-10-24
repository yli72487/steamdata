import csv
import requests
import logging
import time
from typing import Optional

# === Configuration ===
INPUT_CSV       = "steam_all_apps.csv"
OUTPUT_CSV      = "steam_app_content_descriptors.csv"
STORE_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
RATE_LIMIT_SECONDS = 1.0   # delay between requests

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def fetch_content_descriptors(appid: int) -> Optional[str]:
    """Fetches appdetails and returns the 'content_descriptors' value if present, else None."""
    params = {
        "appids": appid,
        "cc": "us",
        "l": "en"
    }
    try:
        resp = requests.get(STORE_DETAILS_URL, params=params)
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
    
    key = str(appid)
    if key not in data or not data[key].get("success", False):
        logger.debug(f"No success data for appid {appid}")
        return None
    
    game_data = data[key]["data"]
    # Attempt to get content_descriptors field
    cd = game_data.get("content_descriptors")
    if cd is None:
        # Possibly a nested descriptor or alternate field
        # You could inspect other fields here if needed
        return None
    return str(cd)

def main(limit: int = 100):
    logger.info(f"Reading up to first {limit} apps from {INPUT_CSV}")
    apps = []
    with open(INPUT_CSV, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            try:
                appid = int(row["appid"])
                name  = row.get("name", "")
            except Exception as e:
                logger.warning(f"Skipping row {i} due to error: {e}")
                continue
            apps.append({"appid": appid, "name": name})
    logger.info(f"Loaded {len(apps)} apps to process.")

    results = []
    for idx, app in enumerate(apps, start=1):
        appid = app["appid"]
        name  = app["name"]
        logger.info(f"[{idx}/{len(apps)}] Fetching content descriptors for: {name} (appid {appid})")
        cd_val = fetch_content_descriptors(appid)
        results.append({
            "rank_index": idx,
            "appid": appid,
            "name": name,
            "content_descriptors": cd_val if cd_val is not None else ""
        })
        time.sleep(RATE_LIMIT_SECONDS)

    logger.info(f"Writing results to {OUTPUT_CSV}")
    with open(OUTPUT_CSV, mode="w", newline='', encoding="utf-8") as f:
        fieldnames = ["rank_index", "appid", "name", "content_descriptors"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    logger.info("Done.")

if __name__ == "__main__":
    main(limit=1000)