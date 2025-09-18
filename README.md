# Oura Sleep iCal

Generate a sleep calendar from your Oura Ring data as an `.ics` file you can import into calendar apps like Google Calendar, Apple Calendar, or Outlook.

## Features

- Fetches sleep data from the Oura API
- Converts sessions into iCalendar format (`.ics`)
- Preserves existing data: Automatically merges new data with existing calendar entries, preventing data loss
- Duplicate prevention: Skips events that already exist in your calendar based on unique IDs
- Includes:
  - Sleep score
  - Time in bed (TIB) and total sleep duration
  - Sleep efficiency
  - Latency and awake time
  - Sleep stage breakdown:
    - REM, light, and deep sleep durations (with % of total sleep)
  - Resting heart rate
- Multiline event summaries and descriptions
- Skips sleep events shorter than a configurable duration (default: 60 minutes)
- Compatible with major calendar clients

## Requirements

- Python 3.8+
- Oura API token with `sleep` and `daily` scopes
- Dependencies:
  - `icalendar`
  - `requests`

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/ramhee98/oura-sleep-ical.git
   cd oura-sleep-ical
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `config.py` or copy `config.py.template` and modify it with:
   ```bash
   cp config.py.template config.py
   ```

## Usage

```bash
python3 main.py
```

This will:
1. Load any existing calendar data from your `sleep.ics` file
2. Fetch new sleep data from the Oura API for the specified number of days
3. Merge the new data with existing events (avoiding duplicates)
4. Save the updated calendar to `sleep.ics`

**Note**: The script automatically preserves your existing sleep data, so you can run it regularly to update your calendar with new entries without losing historical data.

## Example Calendar Output

**Title:**
```
Sleep: 6:48  
Tib: 7:11
```

**Description:**
```
Score: 84
Time in Bed: 7:11
Total Sleep: 6:48
Efficiency: 95%
Latency: 0:08
Awake Time: 0:23
REM Sleep: 1:41 (25%)
Light Sleep: 3:50 (56%)
Deep Sleep: 1:17 (19%)
Resting HR: 54 bpm
```
