"""Tests for database module."""

import json
from datetime import datetime, timezone

import pytest

from vicalerts.database import Database


class TestDatabase:
    """Test database functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create an in-memory database for faster tests."""
        db = Database(":memory:")
        yield db

    def test_init_schema(self, temp_db):
        """Test schema initialization."""
        # Check tables exist
        tables = list(temp_db.db.table_names())
        assert "feeds_raw" in tables
        assert "events" in tables
        assert "event_versions" in tables

    def test_store_raw_feed(self, temp_db):
        """Test storing raw feed data."""
        feed_data = {
            "type": "FeatureCollection",
            "features": [{"id": 1, "data": "test"}],
        }

        feed_id = temp_db.store_raw_feed(feed_data, etag="test-etag")
        assert feed_id > 0

        # Check data was stored
        row = temp_db.db.execute(
            "SELECT * FROM feeds_raw WHERE id = ?", [feed_id]
        ).fetchone()

        assert row is not None
        assert row[2] == "test-etag"  # etag column

    def test_get_raw_feed(self, temp_db):
        """Test retrieving raw feed."""
        original = {"test": "data", "number": 123}
        feed_id = temp_db.store_raw_feed(original)

        retrieved = temp_db.get_raw_feed(feed_id)
        assert retrieved == original

    def test_get_latest_etag(self, temp_db):
        """Test getting latest ETag."""
        # No data yet
        assert temp_db.get_latest_etag() is None

        # Add feeds
        temp_db.store_raw_feed({}, etag="etag1")
        temp_db.store_raw_feed({}, etag="etag2")
        temp_db.store_raw_feed({}, etag=None)  # No ETag

        assert temp_db.get_latest_etag() == "etag2"

    def test_upsert_event(self, temp_db):
        """Test event upsert."""
        now = datetime.now(timezone.utc).isoformat()

        # Insert new event
        temp_db.upsert_event(123, "incident", "CFA", "Fire", "Bushfire", now)

        events = list(temp_db.db["events"].rows)
        assert len(events) == 1
        assert events[0]["event_id"] == 123
        assert events[0]["first_seen"] == now
        assert events[0]["last_seen"] == now

        # Update existing event
        later = datetime.now(timezone.utc).isoformat()
        temp_db.upsert_event(123, "incident", "CFA", "Fire", "Bushfire", later)

        events = list(temp_db.db["events"].rows)
        assert len(events) == 1
        assert events[0]["first_seen"] == now
        assert events[0]["last_seen"] == later

    def test_add_event_version(self, temp_db):
        """Test adding event versions."""
        now = datetime.now(timezone.utc).isoformat()
        temp_db.upsert_event(123, "incident", "CFA", "Fire", "Bushfire", now)

        # Add first version
        props = {"test": "data", "status": "active"}
        result = temp_db.add_event_version(
            123,
            now,
            "active",
            "Test Fire",
            "Fire",
            -37.5,
            144.5,
            "Test Location",
            "Small",
            props,
        )
        assert result is True

        # Try to add same version (should return False)
        result = temp_db.add_event_version(
            123,
            now,
            "active",
            "Test Fire",
            "Fire",
            -37.5,
            144.5,
            "Test Location",
            "Small",
            props,
        )
        assert result is False

        # Add different version
        later = datetime.now(timezone.utc).isoformat()
        result = temp_db.add_event_version(
            123,
            later,
            "contained",
            "Test Fire",
            "Fire",
            -37.5,
            144.5,
            "Test Location",
            "Small",
            props,
        )
        assert result is True

    def test_get_event_versions(self, temp_db):
        """Test retrieving event versions."""
        now = datetime.now(timezone.utc).isoformat()
        temp_db.upsert_event(123, "incident", "CFA", "Fire", "Bushfire", now)

        # Add versions
        props1 = {"version": 1}
        props2 = {"version": 2}

        temp_db.add_event_version(
            123,
            now,
            "active",
            "Fire 1",
            "Fire",
            -37.5,
            144.5,
            "Location 1",
            "Small",
            props1,
        )

        later = datetime.now(timezone.utc).isoformat()
        temp_db.add_event_version(
            123,
            later,
            "contained",
            "Fire 2",
            "Fire",
            -37.6,
            144.6,
            "Location 2",
            "Medium",
            props2,
        )

        # Get versions
        versions = temp_db.get_event_versions(123)
        assert len(versions) == 2
        assert versions[0]["status"] == "active"
        assert versions[0]["raw_props"] == props1
        assert versions[1]["status"] == "contained"
        assert versions[1]["raw_props"] == props2

    def test_compression(self, temp_db):
        """Test data compression."""
        # Create large data
        large_data = {"features": [{"id": i, "data": "x" * 1000} for i in range(100)]}

        feed_id = temp_db.store_raw_feed(large_data)

        # Check compressed size
        row = temp_db.db.execute(
            "SELECT payload FROM feeds_raw WHERE id = ?", [feed_id]
        ).fetchone()

        compressed_size = len(row[0])
        original_size = len(json.dumps(large_data).encode())

        # Should be significantly smaller
        assert compressed_size < original_size / 2

        # Should decompress correctly
        retrieved = temp_db.get_raw_feed(feed_id)
        assert retrieved == large_data

    def test_get_stats(self, temp_db):
        """Test statistics."""
        stats = temp_db.get_stats()
        assert stats["total_feeds"] == 0
        assert stats["total_events"] == 0
        assert stats["total_versions"] == 0

        # Add data
        now = datetime.now(timezone.utc).isoformat()
        temp_db.store_raw_feed({})
        temp_db.upsert_event(1, "incident", "CFA", None, None, now)
        temp_db.upsert_event(2, "warning", "EMV", None, None, now)
        temp_db.add_event_version(
            1, now, "active", None, None, None, None, None, None, {}
        )

        stats = temp_db.get_stats()
        assert stats["total_feeds"] == 1
        assert stats["total_events"] == 2
        assert stats["total_versions"] == 1
        assert stats["events_by_type"]["incident"] == 1
        assert stats["events_by_type"]["warning"] == 1
