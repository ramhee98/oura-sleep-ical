import requests
from datetime import datetime, timedelta
import os

OURA_API_BASE = "https://api.ouraring.com/v2/usercollection/sleep"

def fetch_sleep_data(token: str, days_back: int = 7) -> list:
    """
    Fetch sleep data from Oura API for the past `days_back` days.
    Returns a list of sleep session dictionaries.
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

    response = requests.get(OURA_API_BASE, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("data", [])
