from config import OURA_TOKEN, ICAL_OUTPUT_PATH, DAYS_BACK, MIN_SLEEP_DURATION_MINUTES
from oura_api.client import fetch_sleep_data
from ical.generator import generate_sleep_calendar, save_calendar

def main():
    print(f"Fetching sleep data for the past {DAYS_BACK} days...")
    sleep_data = fetch_sleep_data(OURA_TOKEN, days_back=DAYS_BACK)

    if not sleep_data:
        print("No sleep data found.")
        return

    print(f"Generating calendar with {len(sleep_data)} sleep entries...")
    calendar = generate_sleep_calendar(sleep_data, existing_uids=set(), min_sleep_duration_minutes=MIN_SLEEP_DURATION_MINUTES)

    print(f"Saving calendar to {ICAL_OUTPUT_PATH}...")
    save_calendar(calendar, ICAL_OUTPUT_PATH)

    print("Done.")

if __name__ == "__main__":
    main()