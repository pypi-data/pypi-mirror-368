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
from iss_pass_tracker import get_passes

# Hyderabad coordinates
passes = get_passes(lat=17.385044, lon=78.486671, n=5)
for p in passes:
    print(p.risetime.isoformat(), 'duration', p.duration)
```