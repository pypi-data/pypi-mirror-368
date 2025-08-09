"""Tests for CLI module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from vicalerts.cli import cli


class TestCLI:
    """Test CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_cli_version(self, runner):
        """Test version display."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.2.2" in result.output

    @patch("vicalerts.cli.Poller")
    def test_run_once(self, mock_poller_class, runner):
        """Test run command with --once flag."""
        mock_poller = Mock()
        mock_poller_class.return_value = mock_poller

        result = runner.invoke(cli, ["run", "--once"])

        assert result.exit_code == 0
        mock_poller_class.assert_called_once_with(
            db_path="vicalerts.sqlite", interval=60
        )
        mock_poller.run_once.assert_called_once()
        mock_poller.run.assert_not_called()

    @patch("vicalerts.cli.PollerWithProgress")
    def test_run_continuous(self, mock_poller_class, runner):
        """Test continuous run command."""
        mock_poller = Mock()
        mock_poller_class.return_value = mock_poller

        result = runner.invoke(cli, ["run"])

        assert result.exit_code == 0
        mock_poller_class.assert_called_once_with(
            db_path="vicalerts.sqlite", interval=60
        )
        mock_poller.run.assert_called_once()

    @patch("vicalerts.cli.Poller")
    def test_run_no_progress(self, mock_poller_class, runner):
        """Test run with --no-progress flag."""
        mock_poller = Mock()
        mock_poller_class.return_value = mock_poller

        result = runner.invoke(cli, ["run", "--no-progress"])

        assert result.exit_code == 0
        mock_poller_class.assert_called_once()  # Regular Poller, not PollerWithProgress
        mock_poller.run.assert_called_once()

    def test_run_invalid_interval(self, runner):
        """Test run with invalid interval."""
        result = runner.invoke(cli, ["run", "--interval", "5"])

        assert result.exit_code == 1
        assert "Interval must be at least 10 seconds" in result.output

    @patch("vicalerts.cli.Poller")
    def test_run_custom_options(self, mock_poller_class, runner):
        """Test run with custom options."""
        mock_poller = Mock()
        mock_poller_class.return_value = mock_poller

        result = runner.invoke(
            cli, ["run", "--once", "--interval", "30", "--db", "custom.db"]
        )

        assert result.exit_code == 0
        mock_poller_class.assert_called_once_with(db_path="custom.db", interval=30)

    @patch("vicalerts.cli.PollerWithProgress")
    def test_run_keyboard_interrupt(self, mock_poller_class, runner):
        """Test handling keyboard interrupt."""
        mock_poller = Mock()
        mock_poller.run.side_effect = KeyboardInterrupt()
        mock_poller_class.return_value = mock_poller

        result = runner.invoke(cli, ["run"])

        assert result.exit_code == 0
        assert "Interrupted by user" in result.output

    @patch("vicalerts.cli.PollerWithProgress")
    def test_run_fatal_error(self, mock_poller_class, runner):
        """Test handling fatal error."""
        mock_poller = Mock()
        mock_poller.run.side_effect = Exception("Database error")
        mock_poller_class.return_value = mock_poller

        result = runner.invoke(cli, ["run"])

        assert result.exit_code == 1
        assert "Fatal error: Database error" in result.output

    @patch("vicalerts.database.Database")
    def test_stats_command(self, mock_database_class, runner):
        """Test stats command."""
        mock_db = Mock()
        mock_db.get_stats.return_value = {
            "total_feeds": 100,
            "total_events": 50,
            "total_versions": 200,
            "events_by_type": {"incident": 30, "warning": 20},
        }
        mock_database_class.return_value = mock_db

        # Create a temporary database file
        with runner.isolated_filesystem():
            Path("vicalerts.sqlite").touch()

            result = runner.invoke(cli, ["stats"])

            assert result.exit_code == 0
            assert "Total feeds archived: 100" in result.output
            assert "Total events tracked: 50" in result.output
            assert "Total versions: 200" in result.output
            assert "incident: 30" in result.output
            assert "warning: 20" in result.output

    def test_stats_no_database(self, runner):
        """Test stats command with missing database."""
        with runner.isolated_filesystem():
            # Ensure no database exists
            result = runner.invoke(cli, ["stats"])

            assert result.exit_code == 2  # Click validation error
            assert "Path 'vicalerts.sqlite' does not exist" in result.output

    @patch("vicalerts.database.Database")
    def test_history_command(self, mock_database_class, runner):
        """Test history command."""
        mock_db = Mock()
        mock_db.get_event_versions.return_value = [
            {
                "event_id": 123,
                "version_ts": "2025-01-01T10:00:00Z",
                "status": "active",
                "headline": "Fire at Test Location",
                "location": "Test Location",
                "lat": -37.5,
                "lon": 144.5,
                "size_fmt": "Small",
                "raw_props": {},
            },
            {
                "event_id": 123,
                "version_ts": "2025-01-01T11:00:00Z",
                "status": "contained",
                "headline": "Fire at Test Location",
                "location": "Test Location",
                "lat": -37.5,
                "lon": 144.5,
                "size_fmt": "Small",
                "raw_props": {},
            },
        ]
        mock_database_class.return_value = mock_db

        with runner.isolated_filesystem():
            Path("vicalerts.sqlite").touch()

            result = runner.invoke(cli, ["history", "123"])

            assert result.exit_code == 0
            assert "History for Event 123" in result.output
            assert "Version 1" in result.output
            assert "Version 2" in result.output
            assert "active" in result.output
            assert "contained" in result.output
            assert "-37.500000, 144.500000" in result.output

    @patch("vicalerts.database.Database")
    def test_history_no_event(self, mock_database_class, runner):
        """Test history command with non-existent event."""
        mock_db = Mock()
        mock_db.get_event_versions.return_value = []
        mock_database_class.return_value = mock_db

        with runner.isolated_filesystem():
            Path("vicalerts.sqlite").touch()

            result = runner.invoke(cli, ["history", "999"])

            assert result.exit_code == 1
            assert "No event found with ID: 999" in result.output
