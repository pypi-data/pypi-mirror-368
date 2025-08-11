# iss_pass_tracker/__main__.py
from .api import get_passes, set_api_key
from datetime import datetime
import argparse
import zoneinfo
import os

def main():
    parser = argparse.ArgumentParser(description="Fetch next ISS passes for a given location using N2YO")
    parser.add_argument("--lat", type=float, required=True, help="Latitude in decimal degrees")
    parser.add_argument("--lon", type=float, required=True, help="Longitude in decimal degrees")
    parser.add_argument("--n", type=int, default=5, help="Number of passes to request")
    parser.add_argument("--api-key", type=str, help="N2YO API key")
    parser.add_argument("--all", action="store_true", help="Include all passes, not just visible ones")
    parser.add_argument("--tz", type=str, help="Timezone name (e.g., 'Asia/Kolkata'), defaults to system local time")
    args = parser.parse_args()

    if args.api_key:
        set_api_key(args.api_key)

    tz = None
    if args.tz:
        try:
            tz = zoneinfo.ZoneInfo(args.tz)
        except Exception:
            parser.error(f"Invalid timezone: {args.tz}")

    passes = get_passes(args.lat, args.lon, args.n, visible_only=not args.all)

    if not passes:
        print("No upcoming ISS passes found.")
        return

    print(f"Upcoming ISS passes for lat={args.lat}, lon={args.lon} ({'all' if args.all else 'visible only'}):\n")
    for p in passes:
        local_time = p.local_time(tz)
        local_time_str = local_time.strftime("%Y-%m-%d %I:%M:%S %p %Z")
        print(f"🛰  {local_time_str} — Duration: {p.duration} seconds"
              + (f" — Mag: {p.mag}" if p.mag is not None else ""))

if __name__ == "__main__":
    main()
