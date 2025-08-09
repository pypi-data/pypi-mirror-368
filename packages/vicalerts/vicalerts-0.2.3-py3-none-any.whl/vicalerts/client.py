"""HTTP client for fetching Victoria Emergency feed with conditional GET support."""

import time

import httpx
from rich.console import Console

from .models import GeoJSONFeed

console = Console()

FEED_URL = "https://emergency.vic.gov.au/public/events-geojson.json"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "vicalerts/0.2.3"


class FeedClient:
    """HTTP client for fetching the Victoria Emergency feed."""

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.session = httpx.Client(
            timeout=timeout,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
            },
        )

    def fetch(
        self, etag: str | None = None
    ) -> tuple[GeoJSONFeed | None, str | None, int]:
        """
        Fetch the feed with optional ETag for conditional GET.

        Returns:
            Tuple of (feed_data, new_etag, status_code)
            feed_data is None if status is 304 (Not Modified)
        """
        headers = {}
        if etag:
            headers["If-None-Match"] = etag

        try:
            response = self.session.get(FEED_URL, headers=headers)

            if response.status_code == 304:
                # Not modified
                return None, etag, 304

            response.raise_for_status()

            # Parse response
            data = response.json()
            feed = GeoJSONFeed(**data)

            # Get new ETag
            new_etag = response.headers.get("ETag")

            return feed, new_etag, response.status_code

        except httpx.HTTPStatusError as e:
            console.print(f"[red]HTTP error {e.response.status_code}: {e}")
            raise
        except httpx.RequestError as e:
            console.print(f"[red]Request error: {e}")
            raise
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}")
            raise

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class RetryClient(FeedClient):
    """Feed client with exponential backoff retry logic."""

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ):
        super().__init__(timeout)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def fetch_with_retry(
        self, etag: str | None = None
    ) -> tuple[GeoJSONFeed | None, str | None, int]:
        """Fetch with exponential backoff on failure."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return self.fetch(etag)
            except Exception as e:
                last_error = e

                if attempt < self.max_retries - 1:
                    # Calculate delay with exponential backoff
                    delay = min(self.base_delay * (2**attempt), self.max_delay)
                    console.print(
                        f"[yellow]Retry {attempt + 1}/{self.max_retries} after {delay:.1f}s..."
                    )
                    time.sleep(delay)

        # All retries failed
        raise last_error
