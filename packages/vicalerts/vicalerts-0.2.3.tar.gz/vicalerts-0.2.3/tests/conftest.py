"""Shared test fixtures and configuration."""

from unittest.mock import patch

import pytest


# Speed up tests by making sleep instant
@pytest.fixture(autouse=True)
def fast_sleep():
    """Make time.sleep instant during tests."""
    with patch("time.sleep"):
        yield


@pytest.fixture
def sample_geojson_response():
    """Sample GeoJSON response data."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "feedType": "incident",
                    "sourceOrg": "CFA",
                    "sourceId": "123",
                    "sourceFeed": "test",
                    "id": "123",
                    "category1": "Fire",
                    "category2": "Bushfire",
                    "status": "active",
                    "location": "Test Location",
                    "created": "2025-01-01T10:00:00+10:00",
                    "updated": "2025-01-01T10:00:00+10:00",
                },
                "geometry": {"type": "Point", "coordinates": [144.5, -37.5]},
            }
        ],
        "properties": {"lastUpdated": "2025-01-01T10:00:00Z", "featureCount": 1},
    }
