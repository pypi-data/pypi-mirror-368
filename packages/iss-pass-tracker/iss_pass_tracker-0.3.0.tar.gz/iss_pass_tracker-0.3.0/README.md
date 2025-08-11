# ISS Pass Tracker

A small Python library to fetch upcoming International Space Station (ISS) passes for a given latitude/longitude. Intended as a PyPI-ready example and a practical utility.

## Features
- Query Open Notify (free) for next N passes.
- Return results as typed dataclasses.
- Optional CLI (requires `click` extra).

## Installation (from source / TestPyPI)
```bash
pip install --upgrade pip build twine
python -m build
# Test upload (recommended):
# twine upload --repository testpypi dist/*
# Real upload:
# twine upload dist/*
```

## Quick usage
```python
from iss_pass_tracker import set_api_key, get_passes

# Set your N2YO API key
set_api_key("YOUR_N2YO_API_KEY")

# Hyderabad coordinates
latitude = 17.385044
longitude = 78.486671
altitude_meters = 0  # Adjust if needed

# Get next 5 passes
passes = get_passes(latitude, longitude, altitude_meters, n=5)

# Print them
for p in passes:
    print(f"Pass at {p.local_time()} (local time), duration {p.duration} seconds")
```

## run locally wiith N2YO API key
python check_passes.py

pip install --upgrade iss-pass-tracker


# macOS / Linux
export N2YO_API_KEY="YOUR_KEY"

# Windows (Command Prompt)
setx N2YO_API_KEY "YOUR_KEY"

python -m iss_pass_tracker --lat ... --lon ... 

## run:
python -m iss_pass_tracker --lat 17.385044 --lon 78.486671 --api-key YOUR_N2YO_KEY

or with environment variable

export N2YO_API_KEY=YOUR_N2YO_KEY  # macOS/Linux

set N2YO_API_KEY=YOUR_N2YO_KEY     # Windows

or
If you like, I can also hook this CLI into pyproject.toml so users can just type:


python -m iss_pass_tracker --lat 17.385044 --lon 78.486671

iss-pass-tracker --lat 17.38 --lon 78.48
