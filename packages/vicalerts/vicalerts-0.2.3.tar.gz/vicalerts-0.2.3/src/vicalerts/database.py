"""SQLite database management for Victoria Emergency feed data."""

import gzip
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import sqlite_utils
from rich.console import Console

console = Console()

DEFAULT_DB_PATH = "vicalerts.sqlite"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS feeds_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT NOT NULL,
    etag TEXT,
    payload BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    feed_type TEXT NOT NULL,
    source_org TEXT,
    category1 TEXT,
    category2 TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS event_versions (
    event_id INTEGER NOT NULL,
    version_ts TEXT NOT NULL,
    status TEXT,
    headline TEXT,
    category TEXT,
    lat REAL,
    lon REAL,
    location TEXT,
    size_fmt TEXT,
    raw_props BLOB NOT NULL,
    PRIMARY KEY (event_id, version_ts),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE INDEX IF NOT EXISTS idx_event_versions_event_id ON event_versions(event_id);
CREATE INDEX IF NOT EXISTS idx_events_feed_type ON events(feed_type);
CREATE INDEX IF NOT EXISTS idx_events_last_seen ON events(last_seen);
"""


class Database:
    """Database wrapper for Victoria Emergency data."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db = sqlite_utils.Database(self.db_path)
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        self.db.executescript(SCHEMA_SQL)
        self._migrate_schema()

    def _migrate_schema(self):
        """Apply schema migrations to existing databases."""
        try:
            # Check if is_active column exists
            columns = [col.name for col in self.db["events"].columns]
            if "is_active" not in columns:
                self.db.execute("ALTER TABLE events ADD COLUMN is_active INTEGER DEFAULT 1")
                console.print("[yellow]Migrated database: added is_active column to events table[/yellow]")
        except Exception:
            # If migration fails, continue without is_active support
            pass

    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        with self.db.conn:
            yield self.db

    def store_raw_feed(
        self, feed_data: dict[str, Any], etag: str | None = None, fetched_at: str = None
    ) -> int:
        """Store compressed raw feed data."""
        from datetime import datetime, timezone

        if not fetched_at:
            fetched_at = datetime.now(timezone.utc).isoformat()

        # Compress JSON payload
        json_bytes = json.dumps(feed_data, separators=(",", ":")).encode("utf-8")
        compressed = gzip.compress(json_bytes)

        table = self.db["feeds_raw"]
        row_id = table.insert(
            {"fetched_at": fetched_at, "etag": etag, "payload": compressed}
        ).last_pk

        return row_id

    def get_latest_etag(self) -> str | None:
        """Get the ETag from the most recent successful fetch."""
        result = self.db.execute(
            "SELECT etag FROM feeds_raw WHERE etag IS NOT NULL ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else None
    
    def get_last_sync_time(self) -> str | None:
        """Get the timestamp of the most recent sync."""
        result = self.db.execute(
            "SELECT fetched_at FROM feeds_raw ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else None

    def get_raw_feed(self, feed_id: int) -> dict[str, Any] | None:
        """Retrieve and decompress a raw feed by ID."""
        result = self.db.execute(
            "SELECT payload FROM feeds_raw WHERE id = ?", [feed_id]
        ).fetchone()

        if not result:
            return None

        compressed = result[0]
        json_bytes = gzip.decompress(compressed)
        return json.loads(json_bytes.decode("utf-8"))

    def upsert_event(
        self,
        event_id: int,
        feed_type: str,
        source_org: str,
        category1: str | None,
        category2: str | None,
        timestamp: str,
    ) -> None:
        """Insert or update an event record."""
        table = self.db["events"]

        # Check if event exists
        existing = table.rows_where("event_id = ?", [event_id])
        existing_list = list(existing)

        # Check if is_active column exists for backwards compatibility
        has_is_active = "is_active" in [col.name for col in table.columns]

        if existing_list:
            # Update last_seen and mark as active
            update_data = {"last_seen": timestamp}
            if has_is_active:
                update_data["is_active"] = 1
            table.update(event_id, update_data)
        else:
            # Insert new event
            insert_data = {
                "event_id": event_id,
                "first_seen": timestamp,
                "last_seen": timestamp,
                "feed_type": feed_type,
                "source_org": source_org,
                "category1": category1,
                "category2": category2,
            }
            if has_is_active:
                insert_data["is_active"] = 1
            table.insert(insert_data)

    def add_event_version(
        self,
        event_id: int,
        version_ts: str,
        status: str | None,
        headline: str | None,
        category: str | None,
        lat: float | None,
        lon: float | None,
        location: str | None,
        size_fmt: str | None,
        raw_props: dict[str, Any],
    ) -> bool:
        """Add a new event version if it doesn't exist."""
        table = self.db["event_versions"]

        # Check if this version already exists
        existing = self.db.execute(
            "SELECT 1 FROM event_versions WHERE event_id = ? AND version_ts = ?",
            [event_id, version_ts],
        ).fetchone()

        if existing:
            return False

        # Compress properties
        json_bytes = json.dumps(raw_props, separators=(",", ":")).encode("utf-8")
        compressed = gzip.compress(json_bytes)

        table.insert(
            {
                "event_id": event_id,
                "version_ts": version_ts,
                "status": status,
                "headline": headline,
                "category": category,
                "lat": lat,
                "lon": lon,
                "location": location,
                "size_fmt": size_fmt,
                "raw_props": compressed,
            }
        )

        return True

    def get_event_versions(self, event_id: int) -> list[dict[str, Any]]:
        """Get all versions of an event."""
        results = []

        for row in self.db.execute(
            "SELECT * FROM event_versions WHERE event_id = ? ORDER BY version_ts",
            [event_id],
        ):
            # Decompress properties
            compressed = row[9]  # raw_props column
            json_bytes = gzip.decompress(compressed)
            raw_props = json.loads(json_bytes.decode("utf-8"))

            results.append(
                {
                    "event_id": row[0],
                    "version_ts": row[1],
                    "status": row[2],
                    "headline": row[3],
                    "category": row[4],
                    "lat": row[5],
                    "lon": row[6],
                    "location": row[7],
                    "size_fmt": row[8],
                    "raw_props": raw_props,
                }
            )

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        stats = {
            "total_feeds": self.db.execute("SELECT COUNT(*) FROM feeds_raw").fetchone()[
                0
            ],
            "total_events": self.db.execute("SELECT COUNT(*) FROM events").fetchone()[
                0
            ],
            "total_versions": self.db.execute(
                "SELECT COUNT(*) FROM event_versions"
            ).fetchone()[0],
        }

        # Get events by feed type
        feed_types = {}
        for row in self.db.execute(
            "SELECT feed_type, COUNT(*) FROM events GROUP BY feed_type"
        ):
            feed_types[row[0]] = row[1]
        stats["events_by_type"] = feed_types

        return stats

    def mark_all_inactive(self) -> int:
        """Mark all events as inactive. Returns count of events marked."""
        # Check if is_active column exists
        columns = [col.name for col in self.db["events"].columns]
        if "is_active" not in columns:
            return 0  # No is_active column, nothing to do
        
        result = self.db.execute("UPDATE events SET is_active = 0 WHERE is_active = 1")
        return result.rowcount

    def get_all_events(
        self,
        show_all: bool = False,
        feed_type: str | None = None,
        category: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get all events with their latest version info.
        
        Args:
            show_all: If False (default), only show active events. If True, show all.
            feed_type: Filter by feed type (incident/warning)
            category: Filter by category1
            status: Filter by status
            limit: Limit number of results
            
        Returns:
            List of events with latest version details
        """
        # Check if is_active column exists
        has_is_active = "is_active" in [col.name for col in self.db["events"].columns]
        
        # Build query
        query = """
            SELECT 
                e.event_id,
                e.feed_type,
                e.source_org,
                e.category1,
                e.category2,
                e.last_seen,
                ev.status,
                ev.headline,
                ev.location,
                ev.version_ts
        """
        
        if has_is_active:
            query += ", e.is_active"
            
        query += """
            FROM events e
            JOIN (
                SELECT event_id, MAX(version_ts) as latest_ts
                FROM event_versions
                GROUP BY event_id
            ) latest ON e.event_id = latest.event_id
            JOIN event_versions ev ON e.event_id = ev.event_id 
                AND ev.version_ts = latest.latest_ts
            WHERE 1=1
        """
        
        params = []
        
        # Apply filters
        if not show_all and has_is_active:
            query += " AND e.is_active = 1"
            
        if feed_type:
            query += " AND e.feed_type = ?"
            params.append(feed_type)
            
        if category:
            query += " AND e.category1 = ?"
            params.append(category)
            
        if status:
            query += " AND ev.status = ?"
            params.append(status)
            
        query += " ORDER BY e.last_seen DESC"
        
        if limit:
            query += f" LIMIT {limit}"
            
        results = []
        for row in self.db.execute(query, params):
            event = {
                "event_id": row[0],
                "feed_type": row[1],
                "source_org": row[2],
                "category1": row[3],
                "category2": row[4],
                "last_seen": row[5],
                "status": row[6],
                "headline": row[7],
                "location": row[8],
                "version_ts": row[9],
            }
            if has_is_active:
                event["is_active"] = row[10]
            results.append(event)
            
        return results
