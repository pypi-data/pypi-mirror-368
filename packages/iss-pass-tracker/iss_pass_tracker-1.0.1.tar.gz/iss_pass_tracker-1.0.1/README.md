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

## Quick usage in another file after installing it
```python
import argparse
from iss_pass_tracker import set_api_key, get_passes

parser = argparse.ArgumentParser()
parser.add_argument("--api-key", required=True)
args = parser.parse_args()

# Set the API key for iss_pass_tracker
set_api_key(args.api_key)

lat, lon = 17.385044, 78.486671
passes = get_passes(lat, lon, n=10)

if not passes:
    print("No upcoming ISS passes found.")
else:
    for p in passes:
        # local_time() returns datetime in your system timezone
        print(p.local_time().strftime("%Y-%m-%d %H:%M:%S %Z"), f"for {p.duration} seconds")

```

Run: 
python another_file.py --api-key YOUR_N2YO_KEY

output something like:

2025-08-10 20:42:14 IST for 600 seconds

2025-08-11 19:35:09 IST for 645 seconds
...



## run locally wiith N2YO API key

pip install --upgrade iss-pass-tracker


python -m iss_pass_tracker --lat 17.385044 --lon 78.486671 --api-key YOUR_N2YO_KEY

python -m iss_pass_tracker --lat 17.385044 --lon 78.486671 --api-key YOUR_N2YO_KEY --n 10 --all

The -m flag tells Python: "Run a module as a script."
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
