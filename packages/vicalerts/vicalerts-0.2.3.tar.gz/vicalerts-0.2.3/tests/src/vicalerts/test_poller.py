"""Tests for poller module."""

import signal
from unittest.mock import Mock, patch

import pytest

from vicalerts.poller import Poller, PollerWithProgress


class TestPoller:
    """Test basic poller."""

    @pytest.fixture
    def mock_database(self):
        """Mock database class."""
        with patch("vicalerts.poller.Database") as mock_db:
            yield mock_db

    @pytest.fixture
    def poller(self, mock_database):
        """Create a poller instance."""
        return Poller(interval=10)

    def test_init(self, poller, mock_database):
        """Test poller initialization."""
        assert poller.interval == 10
        assert poller.running is False
        mock_database.assert_called_once_with("vicalerts.sqlite")

    def test_signal_handler(self, poller):
        """Test signal handler sets running to False."""
        poller.running = True
        poller._signal_handler(signal.SIGINT, None)
        assert poller.running is False

    @patch("vicalerts.poller.RetryClient")
    @patch("vicalerts.poller.FeedParser")
    def test_run_once_with_changes(self, mock_parser_class, mock_client_class, poller):
        """Test single poll with changes."""
        # Mock client
        mock_client = Mock()
        mock_feed = Mock()
        mock_client.fetch_with_retry.return_value = (mock_feed, "new-etag", 200)
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Mock parser
        mock_parser = Mock()
        mock_parser.parse_and_store.return_value = {
            "new_events": 2,
            "updated_events": 1,
            "new_versions": 3,
        }
        mock_parser.get_changes_summary.return_value = (
            "2 new events, 1 updated event, 3 changes"
        )
        mock_parser_class.return_value = mock_parser

        # Mock database
        poller.db.get_latest_etag.return_value = "old-etag"
        poller.db.get_stats.return_value = {
            "total_feeds": 10,
            "total_events": 20,
            "total_versions": 30,
            "events_by_type": {"incident": 15, "warning": 5},
        }

        result = poller.run_once()

        assert result is True  # Changes detected
        mock_client.fetch_with_retry.assert_called_once_with("old-etag")
        mock_parser.parse_and_store.assert_called_once_with(mock_feed, "new-etag")

    @patch("vicalerts.poller.RetryClient")
    def test_run_once_not_modified(self, mock_client_class, poller):
        """Test single poll with 304 response."""
        mock_client = Mock()
        mock_client.fetch_with_retry.return_value = (None, "old-etag", 304)
        mock_client_class.return_value.__enter__.return_value = mock_client

        poller.db.get_latest_etag.return_value = "old-etag"

        result = poller.run_once()

        assert result is False  # No changes

    @patch("vicalerts.poller.RetryClient")
    def test_run_once_error(self, mock_client_class, poller):
        """Test single poll with error."""
        mock_client = Mock()
        mock_client.fetch_with_retry.side_effect = Exception("Network error")
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(Exception, match="Network error"):
            poller.run_once()

    @patch("time.sleep")
    @patch("time.time")
    def test_run_continuous(self, mock_time, mock_sleep, poller):
        """Test continuous polling."""
        # Mock time progression - add more values to handle multiple time.time() calls
        mock_time.side_effect = [0, 0.5, 1, 11, 11.5, 12, 22, 22.5, 23]  # Two poll cycles with extra calls

        # Mock run_once
        with patch.object(poller, "run_once") as mock_run_once:
            # Stop after two polls
            def side_effect():
                if mock_run_once.call_count >= 2:
                    poller.running = False
                return True

            mock_run_once.side_effect = side_effect

            poller.run()

            assert mock_run_once.call_count == 2

    def test_show_stats(self, poller, capsys):
        """Test stats display."""
        poller.db.get_stats.return_value = {
            "total_feeds": 10,
            "total_events": 20,
            "total_versions": 30,
            "events_by_type": {"incident": 15, "warning": 5},
        }

        poller._show_stats()

        captured = capsys.readouterr()
        assert "Database Statistics" in captured.out
        assert "10" in captured.out  # total_feeds
        assert "20" in captured.out  # total_events
        assert "30" in captured.out  # total_versions


class TestPollerWithProgress:
    """Test poller with progress display."""

    @pytest.fixture
    def poller(self):
        """Create a progress poller instance."""
        with patch("vicalerts.poller.Database"):
            return PollerWithProgress(interval=5)

    @patch("vicalerts.poller.Live")
    @patch("time.sleep")
    def test_run_with_progress(self, mock_sleep, mock_live_class, poller):
        """Test run with live progress display."""
        mock_live = Mock()
        mock_live_class.return_value.__enter__.return_value = mock_live
        mock_live_class.return_value.__exit__.return_value = None

        # Mock run_once
        with patch.object(poller, "run_once") as mock_run_once:
            mock_run_once.return_value = True  # Changes detected

            # Stop after one poll
            def sleep_side_effect(duration):
                if mock_sleep.call_count >= 3:  # After countdown
                    poller.running = False

            mock_sleep.side_effect = sleep_side_effect

            poller.run()

            # Check live updates
            update_calls = mock_live.update.call_args_list
            assert any("Polling..." in str(call) for call in update_calls)
            assert any("Changes detected" in str(call) for call in update_calls)
            assert any("Next poll in" in str(call) for call in update_calls)
