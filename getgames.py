import requests
import csv
import logging

# === Configuration ===
API_KEY = "CF1B32180826A6A5515524110F3BFD63"  # replace with your key
APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

OUTPUT_CSV = "steam_all_apps.csv"

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# === Fetch app list ===
def fetch_app_list():
    logger.info("Requesting app list from Steam API…")
    params = {"key": API_KEY}
    resp = requests.get(APP_LIST_URL, params=params)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch app list: status {resp.status_code}")
    data = resp.json()
    apps = data.get("applist", {}).get("apps", [])
    logger.info(f"Fetched {len(apps)} apps.")
    return apps

# === Save to CSV ===
def save_to_csv(apps, filepath: str):
    logger.info(f"Saving {len(apps)} apps to CSV file: {filepath}")
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["appid","name"])
        writer.writeheader()
        for app in apps:
            writer.writerow({"appid": app.get("appid"), "name": app.get("name")})

def main():
    apps = fetch_app_list()
    save_to_csv(apps, OUTPUT_CSV)
    logger.info("Done.")

if __name__ == "__main__":
    main()