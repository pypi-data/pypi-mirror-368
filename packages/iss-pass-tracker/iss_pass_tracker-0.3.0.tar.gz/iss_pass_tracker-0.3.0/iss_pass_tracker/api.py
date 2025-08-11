from __future__ import annotations

import requests
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

_API_KEY: Optional[str] = None
BASE_URL = "https://api.n2yo.com/rest/v1/satellite"


@dataclass
class Pass:
    risetime: datetime  # UTC
    duration: int       # seconds

    def local_time(self, tz=None) -> datetime:
        """Return risetime converted to given tz (zoneinfo.ZoneInfo) or local system tz if None."""
        if tz is None:
            return self.risetime.astimezone()
        return self.risetime.astimezone(tz)


def set_api_key(key: str) -> None:
    """
    Set the N2YO API key globally.
    """
    global _API_KEY
    _API_KEY = key


def get_passes(
    lat: float,
    lon: float,
    alt: int = 0,
    n: int = 5,
    sat_id: int = 25544,
    timeout: int = 10
) -> List[Pass]:
    """
    Get the next ISS passes over a location using the N2YO API.

    :param lat: Latitude in decimal degrees.
    :param lon: Longitude in decimal degrees.
    :param alt: Altitude of the observer in meters (default 0).
    :param n: Number of passes to return.
    :param sat_id: Satellite ID (ISS = 25544 by default).
    :param timeout: HTTP timeout in seconds.
    :return: List[Pass]
    :raises RuntimeError: if API key is not set.
    """
    if not _API_KEY:
        raise RuntimeError(
            "N2YO API key not set. Call set_api_key() or set N2YO_API_KEY environment variable."
        )

    url = f"{BASE_URL}/visualpasses/{sat_id}/{lat}/{lon}/{alt}/{n}/0/&apiKey={_API_KEY}"
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    passes_data = data.get("passes", [])
    results: List[Pass] = []

    for p in passes_data:
        risetime = datetime.fromtimestamp(p["startUTC"], tz=timezone.utc)
        duration = int(p.get("duration", 0))
        results.append(Pass(risetime=risetime, duration=duration))

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch next ISS passes for a given location using N2YO API")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--alt", type=int, default=0, help="Altitude in meters")
    parser.add_argument("--n", type=int, default=5, help="Number of passes to return")
    parser.add_argument("--key", type=str, help="N2YO API key (optional if env var set)")
    args = parser.parse_args()

    if args.key:
        set_api_key(args.key)

    for p in get_passes(args.lat, args.lon, args.alt, args.n):
        print(f"{p.risetime.isoformat()} UTC — duration {p.duration} seconds")
