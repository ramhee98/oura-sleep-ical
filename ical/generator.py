from datetime import datetime, timezone
from typing import List, Dict, Optional
from icalendar import Calendar, Event
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import os

def convert_to_hh_mm(seconds):
    min, _ = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%d:%02d' % (hour, min)

def load_existing_calendar(path: str) -> tuple[Calendar, set[str]]:
    """
    Load an existing calendar file and return the calendar object and a set of existing UIDs.
    Returns a new empty calendar and empty set if file doesn't exist.
    """
    if not os.path.exists(path):
        print(f"No existing calendar found at {path}. Starting fresh.")
        empty_cal = Calendar()
        empty_cal.add('prodid', '-//ramhee98//oura-sleep-ical//EN')
        empty_cal.add('version', '2.0')
        return empty_cal, set()
    
    try:
        with open(path, 'rb') as f:
            existing_cal = Calendar.from_ical(f.read())
        
        # Extract existing UIDs
        existing_uids = set()
        for component in existing_cal.walk():
            if component.name == "VEVENT":
                uid = component.get('uid')
                if uid:
                    existing_uids.add(str(uid))
        
        print(f"Loaded existing calendar with {len(existing_uids)} events.")
        return existing_cal, existing_uids
        
    except Exception as e:
        print(f"Error loading existing calendar: {e}. Starting fresh.")
        empty_cal = Calendar()
        empty_cal.add('prodid', '-//ramhee98//oura-sleep-ical//EN')
        empty_cal.add('version', '2.0')
        return empty_cal, set()

def _resolve_target_tz(tz_name: Optional[str]):
    """Resolve a config-supplied IANA timezone name to a ZoneInfo, or None."""
    if not tz_name:
        return None
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        print(f"⚠️  Unknown TIMEZONE '{tz_name}'; keeping API-provided times.")
        return None


def generate_sleep_calendar(sleep_data: List[Dict], existing_calendar: Calendar, existing_uids: set[str], min_sleep_duration_minutes, tz_name: Optional[str] = None, min_sleep_score: Optional[int] = None) -> Calendar:
    # Start with the existing calendar
    cal = existing_calendar
    target_tz = _resolve_target_tz(tz_name)

    for session in sleep_data:
        # Sleep score filter: drop sessions below the configured threshold.
        # Sessions without a score (e.g. very short naps) are always kept
        # so the duration filter remains the sole gate for them.
        if min_sleep_score is not None:
            score = session.get("score")
            if isinstance(score, (int, float)) and score < min_sleep_score:
                continue
        try:
            start = datetime.fromisoformat(session["bedtime_start"])
            end = datetime.fromisoformat(session["bedtime_end"])
        except Exception as e:
            print(f"Skipping due to invalid time: {e}")
            continue

        # Optionally convert to a user-specified timezone so the calendar
        # always renders in a consistent zone regardless of where the Oura
        # device was when it recorded the session.
        if target_tz is not None:
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            start = start.astimezone(target_tz)
            end = end.astimezone(target_tz)

        duration_minutes = (end - start).total_seconds() / 60
        if duration_minutes < min_sleep_duration_minutes:
            continue

        uid = session.get("id") or str(uuid4())
        if uid in existing_uids:
            print(f"Skipping existing event with UID: {uid}")
            continue

        event = Event()
        event.add('uid', uid)
        event.add('dtstart', start)
        event.add('dtend', end)
        now_utc = datetime.now(timezone.utc)
        event.add('dtstamp', now_utc)
        event.add('created', now_utc)
        event.add('last-modified', now_utc)


        try:
            # Duration from bedtime start to end
            duration_seconds = (end - start).total_seconds()
            duration_str = convert_to_hh_mm(duration_seconds)

            # Total sleep duration
            total_sleep_seconds = session.get("total_sleep_duration", 0)
            total_sleep = convert_to_hh_mm(total_sleep_seconds)

            # Sleep phases
            rem_sleep = convert_to_hh_mm(session.get("rem_sleep_duration", 0))
            light_sleep = convert_to_hh_mm(session.get("light_sleep_duration", 0))
            deep_sleep = convert_to_hh_mm(session.get("deep_sleep_duration", 0))

            # Awake time
            awake_time = convert_to_hh_mm(session.get("awake_time", 0))

            # Sleep efficiency. Oura v2 returns this as an integer percentage
            # (e.g. 87), but historical responses sometimes used a 0..1 fraction.
            # Normalise both so the description never shows things like "0.87%"
            # or "N/A%".
            raw_efficiency = session.get("efficiency")
            if raw_efficiency is None:
                efficiency_str = "N/A"
            elif isinstance(raw_efficiency, (int, float)) and raw_efficiency <= 1:
                efficiency_str = f"{round(raw_efficiency * 100)}%"
            else:
                efficiency_str = f"{raw_efficiency}%"

            # Latency (time to fall asleep)
            latency = convert_to_hh_mm(session.get("latency", 0))

            # Resting heart rate
            resting_hr = session.get("lowest_heart_rate", "N/A")

            # Get durations in seconds
            total_sleep_seconds = session.get("total_sleep_duration", 0)
            deep_sleep_seconds = session.get("deep_sleep_duration", 0)
            rem_sleep_seconds = session.get("rem_sleep_duration", 0)
            light_sleep_seconds = session.get("light_sleep_duration", 0)

            # Avoid division by zero. When total sleep is unknown we drop
            # the percentage suffix entirely rather than printing 'N/A%'.
            if total_sleep_seconds > 0:
                rem_suffix = f" ({round((rem_sleep_seconds / total_sleep_seconds) * 100)}%)"
                light_suffix = f" ({round((light_sleep_seconds / total_sleep_seconds) * 100)}%)"
                deep_suffix = f" ({round((deep_sleep_seconds / total_sleep_seconds) * 100)}%)"
            else:
                rem_suffix = light_suffix = deep_suffix = ""


        except Exception as e:
            print(f"Error parsing session data for UID {uid}: {e}")
            continue

        # Multiline fields
        summary = f"Sleep: {total_sleep}\nTib: {duration_str}"
        description = (
            f"Time in Bed: {duration_str}\n"
            f"Total Sleep: {total_sleep}\n"
            f"Efficiency: {efficiency_str}\n"
            f"Latency: {latency}\n"
            f"Awake Time: {awake_time}\n"
            f"REM Sleep: {rem_sleep}{rem_suffix}\n"
            f"Light Sleep: {light_sleep}{light_suffix}\n"
            f"Deep Sleep: {deep_sleep}{deep_suffix}\n"
            f"Resting HR: {resting_hr} bpm"
        )

        event.add('summary', summary)
        event.add('description', description)

        cal.add_component(event)

    return cal

def save_calendar(calendar: Calendar, path: str):
    with open(path, 'wb') as f:
        f.write(calendar.to_ical())
