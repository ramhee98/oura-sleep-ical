from ics import Calendar, Event
from datetime import datetime
from typing import List, Dict
import textwrap

def convert_to_hh_mm_ss(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%d:%02d:%02d' % (hour, min, sec)
    
def generate_sleep_calendar(sleep_data: List[Dict], existing_uids: set[str]) -> Calendar:
    """
    Generates an iCalendar object from a list of sleep sessions.
    Each sleep session must include 'bedtime_start', 'bedtime_end', and optionally metadata.
    """
    cal = Calendar()

    for session in sleep_data:
        start = datetime.fromisoformat(session["bedtime_start"])
        end = datetime.fromisoformat(session["bedtime_end"])
        duration = end - start

        if session["id"] in existing_uids:
            continue  # skip already included events

        e = Event()
        e.created = datetime.now()
        e.uid = session["id"]
        e.name = f"Sleep: {duration}"
        e.begin = start
        e.end = end
        e.description  = (
            f"Score: {session['readiness']['score']} "
            f"Sleep: {convert_to_hh_mm_ss(session['total_sleep_duration'])} "
            f"Efficiency: {session.get('efficiency', 'N/A')}"
        )

        cal.events.add(e)

    return cal

def save_calendar(new_calendar: Calendar, path: str):
    try:
        with open(path, "r") as f:
            existing_calendar = Calendar(f.read())
    except FileNotFoundError:
        existing_calendar = Calendar()

    # Combine events without duplicates (by uid)
    existing_uids = {e.uid for e in existing_calendar.events}
    for event in new_calendar.events:
        if event.uid not in existing_uids:
            existing_calendar.events.add(event)

    with open(path, "w") as f:
        f.writelines(existing_calendar.serialize_iter())

