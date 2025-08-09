"""Tests for Pydantic models."""

from datetime import datetime

import pytest

from vicalerts.models import (
    CAPInfo,
    Feature,
    FeatureProperties,
    GeoJSONFeed,
    Geometry,
)


class TestModels:
    """Test Pydantic model validation."""

    def test_cap_info_optional_fields(self):
        """Test CAP info with minimal data."""
        cap = CAPInfo()
        assert cap.category is None
        assert cap.event is None

    def test_feature_properties_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValueError):
            FeatureProperties()

    def test_feature_properties_valid(self):
        """Test valid feature properties."""
        props = FeatureProperties(
            feedType="incident",
            sourceOrg="CFA",
            sourceId="123",
            sourceFeed="test",
            id="123",
        )
        assert props.feedType == "incident"
        assert props.sourceOrg == "CFA"

    def test_feature_properties_mixed_types(self):
        """Test properties with mixed ID types."""
        # String IDs
        props1 = FeatureProperties(
            feedType="incident",
            sourceOrg="CFA",
            sourceId="123",
            sourceFeed="test",
            id="123",
        )
        assert props1.sourceId == "123"

        # Integer IDs
        props2 = FeatureProperties(
            feedType="incident",
            sourceOrg="CFA",
            sourceId=123,
            sourceFeed="test",
            id=123,
        )
        assert props2.sourceId == 123

    def test_geometry_types(self):
        """Test different geometry types."""
        # Point
        point = Geometry(type="Point", coordinates=[144.5, -37.5])
        assert point.type == "Point"
        assert point.coordinates == [144.5, -37.5]

        # Polygon
        polygon = Geometry(
            type="Polygon", coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        )
        assert polygon.type == "Polygon"

        # GeometryCollection
        geom_collection = Geometry(
            type="GeometryCollection",
            geometries=[{"type": "Point", "coordinates": [0, 0]}],
        )
        assert geom_collection.type == "GeometryCollection"

    def test_feature_complete(self):
        """Test complete feature."""
        feature = Feature(
            type="Feature",
            properties=FeatureProperties(
                feedType="incident",
                sourceOrg="CFA",
                sourceId="123",
                sourceFeed="test",
                id="123",
                created=datetime.now(),
                updated=datetime.now(),
            ),
            geometry=Geometry(type="Point", coordinates=[144.5, -37.5]),
        )
        assert feature.type == "Feature"
        assert feature.properties.sourceId == "123"
        assert feature.geometry.coordinates == [144.5, -37.5]

    def test_geojson_feed(self):
        """Test complete GeoJSON feed."""
        feed = GeoJSONFeed(
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
                    ),
                )
            ],
        )
        assert feed.type == "FeatureCollection"
        assert len(feed.features) == 1

    def test_extra_fields_allowed(self):
        """Test that extra fields are preserved."""
        props = FeatureProperties(
            feedType="incident",
            sourceOrg="CFA",
            sourceId="123",
            sourceFeed="test",
            id="123",
            customField="custom value",
        )
        assert hasattr(props, "customField")
