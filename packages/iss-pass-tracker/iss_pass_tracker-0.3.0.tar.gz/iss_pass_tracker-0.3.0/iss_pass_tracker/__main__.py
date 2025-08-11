import argparse
from .api import get_passes, set_api_key
import os

def main():
    parser = argparse.ArgumentParser(description="ISS pass tracker using N2YO API")
    parser.add_argument("--lat", type=float, required=True, help="Latitude in decimal degrees")
    parser.add_argument("--lon", type=float, required=True, help="Longitude in decimal degrees")
    parser.add_argument("--n", type=int, default=5, help="Number of passes to retrieve")
    parser.add_argument("--api-key", type=str, help="N2YO API key (optional, will use env N2YO_API_KEY if not set)")

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("N2YO_API_KEY")
    if not api_key:
        print("Error: No API key provided. Use --api-key or set N2YO_API_KEY environment variable.")
        return

    set_api_key(api_key)

    passes = get_passes(args.lat, args.lon, args.n)
    if not passes:
        print("No upcoming ISS passes found.")
        return

    for p in passes:
        print(f"Pass at {p.risetime.isoformat()} UTC, duration {p.duration} seconds")

if __name__ == "__main__":
    main()
