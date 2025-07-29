from datetime import datetime, timezone
from typing import List, Dict
from icalendar import Calendar, Event
from uuid import uuid4

def convert_to_hh_mm(seconds):
    min, _ = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%d:%02d' % (hour, min)

def generate_sleep_calendar(sleep_data: List[Dict], existing_uids: set[str], min_sleep_duration_minutes) -> Calendar:
    cal = Calendar()
    cal.add('prodid', '-//ramhee98//oura-sleep-ical//EN')
    cal.add('version', '2.0')

    for session in sleep_data:
        try:
            start = datetime.fromisoformat(session["bedtime_start"])
            end = datetime.fromisoformat(session["bedtime_end"])
        except Exception as e:
            print(f"Skipping due to invalid time: {e}")
            continue

        duration_minutes = (end - start).total_seconds() / 60
        if duration_minutes < min_sleep_duration_minutes:
            continue

        uid = session.get("id") or str(uuid4())
        if uid in existing_uids:
            continue

        event = Event()
        event.add('uid', uid)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('dtstamp', datetime.now(timezone.utc))
        event.add('created', datetime.now(timezone.utc))


        try:
            duration_str = convert_to_hh_mm((end - start).total_seconds())
            total_sleep = convert_to_hh_mm(session.get("total_sleep_duration", 0))
            efficiency = session.get("efficiency", "N/A")
            score = session.get("readiness", {}).get("score", "N/A")
        except Exception as e:
            print(f"Error parsing session data: {e}")
            continue

        # Multiline fields
        summary = f"Sleep: {total_sleep}\nTib: {duration_str}"
        description = f"Score: {score}\nTime in Bed: {duration_str}\nEfficiency: {efficiency}"

        event.add('summary', summary)
        event.add('description', description)

        cal.add_component(event)

    return cal

def save_calendar(calendar: Calendar, path: str):
    with open(path, 'wb') as f:
        f.write(calendar.to_ical())
