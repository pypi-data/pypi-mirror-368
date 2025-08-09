"""Script to fetch and analyze the Victoria Emergency feed structure."""

from pprint import pprint

import httpx

from .models import GeoJSONFeed


def probe_feed():
    """Fetch feed and print discovered keys."""
    response = httpx.get("https://emergency.vic.gov.au/public/events-geojson.json")
    data = response.json()

    # Extract all unique property keys
    all_keys = set()
    for feature in data["features"]:
        all_keys.update(feature["properties"].keys())

    print(f"Top-level keys: {list(data.keys())}")
    print(f"\nUnique property keys ({len(all_keys)}): {sorted(all_keys)}")

    # Validate with our model
    try:
        feed = GeoJSONFeed(**data)
        print(f"\n✓ Model validation successful! {len(feed.features)} features found.")
    except Exception as e:
        print(f"\n✗ Model validation failed: {e}")

    # Show sample feature
    if data["features"]:
        print("\nSample feature properties:")
        pprint(data["features"][0]["properties"], width=120, compact=True)


if __name__ == "__main__":
    probe_feed()
