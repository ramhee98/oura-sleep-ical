from ics import Calendar, Event
from datetime import datetime
from typing import List, Dict
import textwrap

def convert_to_hh_mm(seconds):
    min, _ = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%d:%02d' % (hour, min)
    
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
        duration = convert_to_hh_mm(duration.total_seconds())

        if session["id"] in existing_uids:
            continue  # skip already included events

        e = Event()
        e.created = datetime.now()
        e.uid = session["id"]
        e.name = f"Tib: {duration}"
        e.begin = start
        e.end = end

        try:
            score = session['readiness']['score']
        except:
            score = 'N/A'
            print(f"Error parsing date for session {session['id']}")

        try:
            total_sleep_duration = convert_to_hh_mm(session['total_sleep_duration'])
            e.name = f"Sleep: {total_sleep_duration}"
        except:
            total_sleep_duration = 'N/A'
            print(f"Error parsing date for session {session['id']}")

        try:
            efficiency = session.get('efficiency', 'N/A')
        except:
            efficiency = 'N/A'
            print(f"Error parsing date for session {session['id']}")

        e.description  = (
            f"Score: {score} "
            f"Time in Bed: {duration} "
            f"Efficiency: {efficiency}"
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

    existing_calendar.serialize_iter()
    existing_calendar = existing_calendar.serialize().replace(
        "PRODID:ics.py - http://git.io/lLljaA", 
        "PRODID:-//ramhee98//oura-sleep-ical//EN"
    )

    with open(path, "w") as f:
        f.writelines(existing_calendar)
