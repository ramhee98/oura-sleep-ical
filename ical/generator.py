from ics import Calendar, Event
from datetime import datetime
from typing import List, Dict

def convert_to_hh_mm_ss(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%d:%02d:%02d' % (hour, min, sec)
    
def generate_sleep_calendar(sleep_data: List[Dict]) -> Calendar:
    """
    Generates an iCalendar object from a list of sleep sessions.
    Each sleep session must include 'bedtime_start', 'bedtime_end', and optionally metadata.
    """
    cal = Calendar()

    for session in sleep_data:
        start = datetime.fromisoformat(session["bedtime_start"])
        end = datetime.fromisoformat(session["bedtime_end"])
        duration = end - start

        e = Event()
        e.name = f"Sleep: {duration}"
        e.begin = start
        e.end = end
        e.description = (
            f"Sleep Score: {session['readiness']['score'], 'N/A'}\n"
            f"Actual Sleep: {convert_to_hh_mm_ss(session['total_sleep_duration'])}\n"
            f"Efficiency: {session.get('efficiency', 'N/A')}"
        )

        cal.events.add(e)

    return cal

def save_calendar(cal: Calendar, output_path: str):
    with open(output_path, 'w') as f:
        f.writelines(cal)
