# Oura Sleep iCal

Generate a sleep calendar from your Oura Ring data as an `.ics` file you can import into calendar apps.

## Features

- Fetches sleep data from the Oura API
- Converts sessions into iCalendar format (`.ics`)
- Includes sleep score, time in bed duration, and efficiency in event descriptions

## Requirements

- Python 3.8+
- Oura API token with `sleep` and `daily` scopes
- `ics` library

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

This will output a file like `sleep.ics` in the project directory.

## License

MIT
