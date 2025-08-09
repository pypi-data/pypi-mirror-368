"""Tests for parser module."""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from vicalerts.database import Database
from vicalerts.models import Feature, FeatureProperties, GeoJSONFeed, Geometry
from vicalerts.parser import FeedParser


class TestFeedParser:
    """Test feed parser."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def parser(self, mock_db):
        """Create a parser instance."""
        return FeedParser(mock_db)

    @pytest.fixture
    def sample_feed(self):
        """Create a sample feed."""
        return GeoJSONFeed(
            type="FeatureCollection",
            features=[
                Feature(
                    type="Feature",
                    properties=FeatureProperties(
                        feedType="incident",
                        sourceOrg="CFA",
                        sourceId="123",
                        sourceFeed="test",
                        id="123",
                        category1="Fire",
                        category2="Bushfire",
                        status="active",
                        location="Test Location",
                        updated=datetime.now(timezone.utc),
                    ),
                    geometry=Geometry(type="Point", coordinates=[144.5, -37.5]),
                )
            ],
        )

    def test_parse_and_store(self, parser, mock_db, sample_feed):
        """Test parsing and storing feed."""
        # Mock transaction context
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_db)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)

        # Mock database operations
        mock_db.db = {"events": Mock()}
        mock_db.db["events"].rows_where.return_value = []  # No existing events
        mock_db.db["events"].columns = []  # No is_active column for backwards compatibility
        mock_db.add_event_version.return_value = True  # New version
        mock_db.mark_all_inactive.return_value = 0  # No events to deactivate

        stats = parser.parse_and_store(sample_feed, etag="test-etag")

        assert stats["new_events"] == 1
        assert stats["updated_events"] == 0
        assert stats["new_versions"] == 1
        assert stats["deactivated_events"] == 0

        # Check database calls
        mock_db.store_raw_feed.assert_called_once()
        mock_db.mark_all_inactive.assert_called_once()
        mock_db.upsert_event.assert_called_once_with(
            event_id=123,
            feed_type="incident",
            source_org="CFA",
            category1="Fire",
            category2="Bushfire",
            timestamp=mock_db.store_raw_feed.call_args[1]["fetched_at"],
        )
        mock_db.add_event_version.assert_called_once()

    def test_process_feature_new_event(self, parser, mock_db):
        """Test processing a new event."""
        feature = Feature(
            type="Feature",
            properties=FeatureProperties(
                feedType="incident",
                sourceOrg="CFA",
                sourceId="456",
                sourceFeed="test",
                id="456",
                updated=datetime.now(timezone.utc),
                status="active",
                location="New Location",
            ),
        )

        mock_db.db = {"events": Mock()}
        mock_db.db["events"].rows_where.return_value = []  # No existing
        mock_db.add_event_version.return_value = True

        is_new, is_new_version = parser._process_feature(
            feature, datetime.now().isoformat()
        )

        assert is_new is True
        assert is_new_version is True

    def test_process_feature_existing_event(self, parser, mock_db):
        """Test processing an existing event."""
        feature = Feature(
            type="Feature",
            properties=FeatureProperties(
                feedType="incident",
                sourceOrg="CFA",
                sourceId="789",
                sourceFeed="test",
                id="789",
                updated=datetime.now(timezone.utc),
            ),
        )

        mock_db.db = {"events": Mock()}
        mock_db.db["events"].rows_where.return_value = [{"event_id": 789}]  # Existing
        mock_db.add_event_version.return_value = False  # No new version

        is_new, is_new_version = parser._process_feature(
            feature, datetime.now().isoformat()
        )

        assert is_new is False
        assert is_new_version is False

    def test_extract_coordinates_point(self, parser):
        """Test coordinate extraction from Point geometry."""
        feature = Feature(
            type="Feature",
            properties=FeatureProperties(
                feedType="incident",
                sourceOrg="CFA",
                sourceId="1",
                sourceFeed="test",
                id="1",
            ),
            geometry=Geometry(type="Point", coordinates=[144.5, -37.5]),
        )

        lat, lon = parser._extract_coordinates(feature)
        assert lat == -37.5
        assert lon == 144.5

    def test_extract_coordinates_polygon(self, parser):
        """Test coordinate extraction from Polygon geometry."""
        feature = Feature(
            type="Feature",
            properties=FeatureProperties(
                feedType="incident",
                sourceOrg="CFA",
                sourceId="1",
                sourceFeed="test",
                id="1",
            ),
            geometry=Geometry(
                type="Polygon", coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
            ),
        )

        lat, lon = parser._extract_coordinates(feature)
        assert lat == 0.4  # Centroid (includes closing point)
        assert lon == 0.4

    def test_extract_coordinates_geometry_collection(self, parser):
        """Test coordinate extraction from GeometryCollection."""
        feature = Feature(
            type="Feature",
            properties=FeatureProperties(
                feedType="incident",
                sourceOrg="CFA",
                sourceId="1",
                sourceFeed="test",
                id="1",
            ),
            geometry=Geometry(
                type="GeometryCollection",
                geometries=[
                    {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]],
                    },
                    {"type": "Point", "coordinates": [144.5, -37.5]},
                ],
            ),
        )

        lat, lon = parser._extract_coordinates(feature)
        assert lat == -37.5  # From first Point
        assert lon == 144.5

    def test_extract_coordinates_no_geometry(self, parser):
        """Test coordinate extraction with no geometry."""
        feature = Feature(
            type="Feature",
            properties=FeatureProperties(
                feedType="incident",
                sourceOrg="CFA",
                sourceId="1",
                sourceFeed="test",
                id="1",
            ),
        )

        lat, lon = parser._extract_coordinates(feature)
        assert lat is None
        assert lon is None

    def test_extract_headline_priority(self, parser):
        """Test headline extraction priority."""
        # webHeadline takes priority
        props = FeatureProperties(
            feedType="incident",
            sourceOrg="CFA",
            sourceId="1",
            sourceFeed="test",
            id="1",
            webHeadline="Web Headline",
            sourceTitle="Source Title",
            name="Name",
            text="Text headline\nMore text",
        )
        assert parser._extract_headline(props) == "Web Headline"

        # sourceTitle if no webHeadline
        props.webHeadline = None
        assert parser._extract_headline(props) == "Source Title"

        # name + location if available
        props.sourceTitle = None
        props.location = "Test Location"
        assert parser._extract_headline(props) == "Name - Test Location"

        # Just name if no location
        props.location = None
        assert parser._extract_headline(props) == "Name"

        # First line of text as fallback
        props.name = None
        assert parser._extract_headline(props) == "Text headline"

        # None if nothing available
        props.text = None
        assert parser._extract_headline(props) is None

    def test_get_changes_summary(self, parser):
        """Test changes summary formatting."""
        assert (
            parser.get_changes_summary(
                {"new_events": 0, "updated_events": 0, "new_versions": 0}
            )
            == "No changes detected"
        )

        assert (
            parser.get_changes_summary(
                {"new_events": 1, "updated_events": 0, "new_versions": 1}
            )
            == "1 new event, 1 change"
        )

        assert (
            parser.get_changes_summary(
                {"new_events": 2, "updated_events": 3, "new_versions": 5}
            )
            == "2 new events, 3 updated events, 5 changes"
        )
