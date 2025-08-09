"""Parser for Victoria Emergency feed with change detection."""

import json
from datetime import datetime, timezone

from rich.console import Console

from .database import Database
from .models import Feature, GeoJSONFeed

console = Console()


class FeedParser:
    """Parse feed and detect changes."""

    def __init__(self, database: Database):
        self.db = database

    def parse_and_store(
        self, feed: GeoJSONFeed, etag: str | None = None
    ) -> dict[str, int]:
        """
        Parse feed and store changes.

        Returns:
            Dict with counts: new_events, updated_events, new_versions, deactivated_events
        """
        stats = {"new_events": 0, "updated_events": 0, "new_versions": 0, "deactivated_events": 0}

        # Store raw feed
        now = datetime.now(timezone.utc).isoformat()
        feed_dict = feed.model_dump_json()  # Serialize to JSON string first
        feed_dict = json.loads(feed_dict)  # Then parse back to dict
        self.db.store_raw_feed(feed_dict, etag=etag, fetched_at=now)

        # Mark all events as inactive before processing
        with self.db.transaction():
            deactivated_count = self.db.mark_all_inactive()

            # Process each feature
            for feature in feed.features:
                new_event, new_version = self._process_feature(feature, now)

                if new_event:
                    stats["new_events"] += 1
                else:
                    stats["updated_events"] += 1

                if new_version:
                    stats["new_versions"] += 1

            # Count events that remain inactive (were removed from feed)
            if deactivated_count > 0:
                # Check if is_active column exists
                columns = [col.name for col in self.db.db["events"].columns]
                if "is_active" in columns:
                    result = self.db.db.execute("SELECT COUNT(*) FROM events WHERE is_active = 0").fetchone()
                    stats["deactivated_events"] = result[0] if result else 0

        return stats

    def _process_feature(self, feature: Feature, timestamp: str) -> tuple[bool, bool]:
        """
        Process a single feature.

        Returns:
            Tuple of (is_new_event, is_new_version)
        """
        props = feature.properties

        # Convert sourceId to int for database if possible, otherwise hash it
        try:
            event_id = (
                int(props.sourceId)
                if isinstance(props.sourceId, str)
                else props.sourceId
            )
        except ValueError:
            # For non-numeric IDs, use a hash
            event_id = hash(props.sourceId) & 0x7FFFFFFF  # Keep it positive and 32-bit

        # Check if event exists
        existing = list(self.db.db["events"].rows_where("event_id = ?", [event_id]))
        is_new = not existing

        # Upsert event
        self.db.upsert_event(
            event_id=event_id,
            feed_type=props.feedType,
            source_org=props.sourceOrg,
            category1=props.category1,
            category2=props.category2,
            timestamp=timestamp,
        )

        # Extract version timestamp
        version_ts = props.updated.isoformat() if props.updated else timestamp

        # Extract location data
        lat, lon = self._extract_coordinates(feature)

        # Determine headline
        headline = self._extract_headline(props)

        # Determine category
        category = props.category1 or props.feedType

        # Add event version
        is_new_version = self.db.add_event_version(
            event_id=event_id,
            version_ts=version_ts,
            status=props.status,
            headline=headline,
            category=category,
            lat=lat,
            lon=lon,
            location=props.location,
            size_fmt=props.sizeFmt,
            raw_props=json.loads(
                props.model_dump_json()
            ),  # Serialize then parse for datetime handling
        )

        return is_new, is_new_version

    def _extract_coordinates(
        self, feature: Feature
    ) -> tuple[float | None, float | None]:
        """Extract lat/lon from feature geometry."""
        if not feature.geometry:
            return None, None

        geom = feature.geometry

        if geom.type == "Point" and geom.coordinates:
            # [lon, lat] in GeoJSON
            if len(geom.coordinates) >= 2:
                return geom.coordinates[1], geom.coordinates[0]

        elif geom.type == "Polygon" and geom.coordinates:
            # Get centroid of first ring
            if geom.coordinates and geom.coordinates[0]:
                ring = geom.coordinates[0]
                if ring:
                    lons = [coord[0] for coord in ring]
                    lats = [coord[1] for coord in ring]
                    return sum(lats) / len(lats), sum(lons) / len(lons)

        elif geom.type == "GeometryCollection" and geom.geometries:
            # Look for first Point geometry
            for sub_geom in geom.geometries:
                if sub_geom.get("type") == "Point":
                    coords = sub_geom.get("coordinates", [])
                    if len(coords) >= 2:
                        return coords[1], coords[0]

        return None, None

    def _extract_headline(self, props) -> str | None:
        """Extract most appropriate headline from properties."""
        # Priority order for headline
        if props.webHeadline:
            return props.webHeadline

        if props.sourceTitle:
            return props.sourceTitle

        if props.name and props.location:
            return f"{props.name} - {props.location}"

        if props.name:
            return props.name

        if props.text:
            # Extract first line
            lines = props.text.strip().split("\n")
            if lines:
                return lines[0][:200]  # Limit length

        return None

    def get_changes_summary(self, stats: dict[str, int]) -> str:
        """Format a summary of changes."""
        parts = []

        if stats["new_events"]:
            parts.append(
                f"{stats['new_events']} new event{'s' if stats['new_events'] != 1 else ''}"
            )

        if stats["updated_events"]:
            parts.append(
                f"{stats['updated_events']} updated event{'s' if stats['updated_events'] != 1 else ''}"
            )

        if stats["new_versions"]:
            parts.append(
                f"{stats['new_versions']} change{'s' if stats['new_versions'] != 1 else ''}"
            )

        if stats.get("deactivated_events"):
            parts.append(
                f"{stats['deactivated_events']} event{'s' if stats['deactivated_events'] != 1 else ''} removed"
            )

        if not parts:
            return "No changes detected"

        return ", ".join(parts)
