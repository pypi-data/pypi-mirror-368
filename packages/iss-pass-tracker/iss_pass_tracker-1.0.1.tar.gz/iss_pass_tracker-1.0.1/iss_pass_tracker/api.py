from __future__ import annotations

import os
import requests
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

# N2YO API endpoints
N2YO_BASE = "https://api.n2yo.com/rest/v1/satellite"
ALL_PASSES_ENDPOINT = N2YO_BASE + "/predictions/{sat_id}/{lat}/{lon}/0/{n}/&apiKey={api_key}"
VISIBLE_PASSES_ENDPOINT = N2YO_BASE + "/visualpasses/{sat_id}/{lat}/{lon}/0/{n}/&apiKey={api_key}"

# ISS NORAD ID
ISS_ID = 25544

@dataclass
class Pass:
    risetime: datetime  # UTC
    duration: int       # seconds
    mag: Optional[float] = None  # magnitude (only for visible passes)

    def local_time(self, tz=None) -> datetime:
        """Return risetime converted to given tz (zoneinfo.ZoneInfo) or local system tz if None."""
        if tz is None:
            return self.risetime.astimezone()
        return self.risetime.astimezone(tz)


_api_key: Optional[str] = None

def set_api_key(key: str) -> None:
    """Set the N2YO API key for future requests."""
    global _api_key
    _api_key = key


def _get_api_key() -> str:
    """Get API key from set value or environment variable."""
    key = _api_key or os.getenv("N2YO_API_KEY")
    if not key:
        raise ValueError("No API key provided. Use set_api_key() or set N2YO_API_KEY env variable.")
    return key


def get_passes(lat: float, lon: float, n: int = 5, visible_only: bool = True, timeout: int = 10) -> List[Pass]:
    """
    Query N2YO API to return next `n` ISS passes for given coordinates.

    :param lat: Latitude in decimal degrees
    :param lon: Longitude in decimal degrees
    :param n: Number of passes to request
    :param visible_only: Whether to return only visible passes
    :param timeout: HTTP request timeout in seconds
    :return: List of Pass objects
    """
    api_key = _get_api_key()

    if visible_only:
        url = VISIBLE_PASSES_ENDPOINT.format(sat_id=ISS_ID, lat=lat, lon=lon, n=n, api_key=api_key)
    else:
        url = ALL_PASSES_ENDPOINT.format(sat_id=ISS_ID, lat=lat, lon=lon, n=n, api_key=api_key)

    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for entry in data.get("passes", []):
        risetime = datetime.fromtimestamp(entry["startUTC"], tz=timezone.utc)
        duration = int(entry.get("duration", 0))
        mag = entry.get("mag")
        items.append(Pass(risetime=risetime, duration=duration, mag=mag))

    return items


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch next ISS passes for a given location using N2YO")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--api-key", type=str)
    parser.add_argument("--all", action="store_true", help="Include all passes, not just visible ones")
    args = parser.parse_args()

    if args.api_key:
        set_api_key(args.api_key)

    passes = get_passes(args.lat, args.lon, args.n, visible_only=not args.all)
    if not passes:
        print("No upcoming ISS passes found.")
    else:
        for p in passes:
            print(f"{p.risetime.isoformat()} duration {p.duration}s mag={p.mag}")
