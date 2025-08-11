from __future__ import annotations

import requests
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

OPEN_NOTIFY_URL = "http://api.open-notify.org/iss-pass.json"

@dataclass
class Pass:
    risetime: datetime  # UTC
    duration: int       # seconds

    def local_time(self, tz=None) -> datetime:
        """Return risetime converted to given tz (zoneinfo.ZoneInfo) or local system tz if None."""
        if tz is None:
            return self.risetime.astimezone()
        return self.risetime.astimezone(tz)


def get_passes(lat: float, lon: float, n: int = 5, timeout: int = 10) -> List[Pass]:
    """
    Query the Open Notify API to return the next `n` ISS passes for the given coordinates.

    :param lat: Latitude in decimal degrees (e.g., 17.385044)
    :param lon: Longitude in decimal degrees (e.g., 78.486671)
    :param n: Number of passes to request (API supports up to some small limit)
    :param timeout: HTTP request timeout in seconds
    :return: List[Pass]
    """
    params = {"lat": lat, "lon": lon, "n": n}
    resp = requests.get(OPEN_NOTIFY_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    # The API returns `response` list with objects like {"risetime": 1596564000, "duration": 600}
    items = []
    for item in data.get("response", []):
        risetime = datetime.fromtimestamp(item["risetime"], tz=timezone.utc)
        duration = int(item.get("duration", 0))
        items.append(Pass(risetime=risetime, duration=duration))
    return items


if __name__ == "__main__":
    # quick demo when run as a script
    import argparse
    parser = argparse.ArgumentParser(description="Fetch next ISS passes for a given location")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()

    for p in get_passes(args.lat, args.lon, args.n):
        print(p.risetime.isoformat(), "duration", p.duration)
