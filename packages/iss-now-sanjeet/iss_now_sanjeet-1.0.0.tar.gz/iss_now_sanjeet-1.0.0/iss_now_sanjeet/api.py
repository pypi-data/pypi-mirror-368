# iss_pass_tracker/api.py
import requests
from datetime import datetime, timezone

def get_current_location():
    """Fetch the current ISS position from Open Notify API."""
    url = "http://api.open-notify.org/iss-now.json"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    lat = float(data["iss_position"]["latitude"])
    lon = float(data["iss_position"]["longitude"])
    ts = datetime.fromtimestamp(data["timestamp"], tz=timezone.utc)

    return lat, lon, ts
