"""Tests for HTTP client module."""

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from vicalerts.client import FeedClient, RetryClient
from vicalerts.models import GeoJSONFeed


class TestFeedClient:
    """Test basic feed client."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock HTTP session."""
        return MagicMock()

    @pytest.fixture
    def client(self, mock_session):
        """Create a client instance with mocked session."""
        with patch("httpx.Client", return_value=mock_session):
            client = FeedClient()
            yield client

    def test_init(self):
        """Test client initialization."""
        with patch("httpx.Client"):
            client = FeedClient()
            assert client.timeout == 30.0

    def test_fetch_success(self, client, sample_geojson_response):
        """Test successful fetch."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_geojson_response
        mock_response.headers = {"ETag": "new-etag"}
        client.session.get.return_value = mock_response

        feed, etag, status = client.fetch()

        assert isinstance(feed, GeoJSONFeed)
        assert etag == "new-etag"
        assert status == 200

    def test_fetch_with_etag(self, client):
        """Test fetch with ETag."""
        mock_response = Mock()
        mock_response.status_code = 304
        client.session.get.return_value = mock_response

        feed, etag, status = client.fetch(etag="old-etag")

        assert feed is None
        assert etag == "old-etag"
        assert status == 304

        # Check ETag header was sent
        client.session.get.assert_called_once()
        call_args = client.session.get.call_args
        assert call_args[1]["headers"]["If-None-Match"] == "old-etag"

    def test_fetch_http_error(self, client):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=Mock(), response=mock_response
        )
        client.session.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            client.fetch()

    def test_fetch_network_error(self, client):
        """Test network error handling."""
        client.session.get.side_effect = httpx.RequestError("Network error")

        with pytest.raises(httpx.RequestError):
            client.fetch()

    def test_context_manager(self):
        """Test client as context manager."""
        with patch("httpx.Client") as mock_client_class:
            mock_session = MagicMock()
            mock_client_class.return_value = mock_session

            with FeedClient() as client:
                assert client.session is not None

            # Session should be closed
            mock_session.close.assert_called_once()


class TestRetryClient:
    """Test retry client."""

    @pytest.fixture
    def client(self):
        """Create a retry client with mocked session."""
        with patch("httpx.Client") as mock_client_class:
            mock_session = MagicMock()
            mock_client_class.return_value = mock_session
            client = RetryClient(max_retries=3, base_delay=0.01, max_delay=0.1)
            # Ensure the session is the mock
            client.session = mock_session
            return client

    def test_fetch_with_retry_success(self, client, sample_geojson_response):
        """Test successful fetch without retries."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_geojson_response
        mock_response.headers = {}

        client.session.get.return_value = mock_response
        feed, etag, status = client.fetch_with_retry()

        assert isinstance(feed, GeoJSONFeed)
        assert client.session.get.call_count == 1

    def test_fetch_with_retry_eventual_success(self, client, sample_geojson_response):
        """Test retry succeeds after failures."""
        # First two calls fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=Mock(), response=Mock(status_code=500)
        )

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = sample_geojson_response
        mock_response_success.headers = {}

        client.session.get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        feed, etag, status = client.fetch_with_retry()

        assert isinstance(feed, GeoJSONFeed)
        assert client.session.get.call_count == 3

    def test_fetch_with_retry_all_fail(self, client):
        """Test all retries fail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=Mock(), response=Mock(status_code=500)
        )

        client.session.get.return_value = mock_response
        with pytest.raises(httpx.HTTPStatusError):
            client.fetch_with_retry()

        assert client.session.get.call_count == 3
