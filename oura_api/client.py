import requests
from datetime import datetime, timedelta
import os

OURA_API_BASE = "https://api.ouraring.com/v2/usercollection/sleep"

def fetch_sleep_data(token: str, days_back: int = 7) -> list:
    """
    Fetch sleep data from Oura API for the past `days_back` days.
    Returns a list of sleep session dictionaries.

    Returns an empty list (and prints a friendly message) on network errors,
    auth failures, or malformed responses, instead of raising.
    """
    headers = {
        "Authorization": f"Bearer {token}"
    }

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }

    try:
        response = requests.get(OURA_API_BASE, headers=headers, params=params, timeout=30)
    except requests.RequestException as e:
        print(f"❌ Could not reach the Oura API: {e}")
        return []

    if response.status_code == 401:
        print("❌ Oura API rejected the access token (HTTP 401). "
              "Check OURA_TOKEN in config.py.")
        return []
    if response.status_code == 429:
        print("❌ Oura API rate limit hit (HTTP 429). Try again later.")
        return []
    if not response.ok:
        print(f"❌ Oura API returned HTTP {response.status_code}: {response.text[:200]}")
        return []

    try:
        data = response.json()
    except ValueError:
        print("❌ Oura API returned a non-JSON response.")
        return []

    return data.get("data", [])
