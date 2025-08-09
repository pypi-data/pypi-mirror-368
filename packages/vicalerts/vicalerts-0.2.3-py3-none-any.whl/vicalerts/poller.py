"""Main polling loop for Victoria Emergency feed."""

import signal
import time
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from .client import RetryClient
from .database import Database
from .parser import FeedParser

console = Console()


class Poller:
    """Main polling loop with signal handling."""

    def __init__(self, db_path: str = "vicalerts.sqlite", interval: int = 60):
        self.db = Database(db_path)
        self.interval = interval
        self.running = False
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Set up graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        console.print("\n[yellow]Received shutdown signal, stopping gracefully...")
        self.running = False

    def run_once(self) -> bool:
        """Run a single poll cycle. Returns True if changes were detected."""
        with RetryClient() as client:
            parser = FeedParser(self.db)

            # Get last ETag
            etag = self.db.get_latest_etag()

            # Fetch feed
            console.print(f"[blue]Fetching feed... (ETag: {etag or 'none'})")

            try:
                feed, new_etag, status = client.fetch_with_retry(etag)

                if status == 304:
                    console.print("[green]Feed not modified (304)")
                    return False

                # Parse and store changes
                stats = parser.parse_and_store(feed, new_etag)
                summary = parser.get_changes_summary(stats)

                console.print(f"[green]✓ {summary}")

                # Show current stats
                self._show_stats()

                return stats["new_versions"] > 0

            except Exception as e:
                console.print(f"[red]Error: {e}")
                raise

    def run(self):
        """Run continuous polling loop."""
        console.print(
            Panel.fit(
                "[bold green]VicAlerts[/bold green]\n"
                f"Polling every {self.interval} seconds\n"
                "Press Ctrl+C to stop",
                border_style="green",
            )
        )

        self.running = True
        last_poll = 0

        try:
            while self.running:
                now = time.time()

                if now - last_poll >= self.interval:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(f"\n[dim]{timestamp}[/dim]")

                    try:
                        self.run_once()
                    except Exception as e:
                        console.print(f"[red]Poll failed: {e}")

                    last_poll = now
                else:
                    # Sleep for a short time to avoid busy waiting
                    time.sleep(0.5)

        except KeyboardInterrupt:
            pass

        console.print("\n[green]Poller stopped.")

    def _show_stats(self):
        """Display current database statistics."""
        stats = self.db.get_stats()

        table = Table(title="Database Statistics", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total feeds", str(stats["total_feeds"]))
        table.add_row("Total events", str(stats["total_events"]))
        table.add_row("Total versions", str(stats["total_versions"]))

        for feed_type, count in stats["events_by_type"].items():
            table.add_row(f"  {feed_type}", str(count))

        console.print(table)


class PollerWithProgress(Poller):
    """Poller with live progress display."""

    def run(self):
        """Run with live countdown display."""
        console.print(
            Panel.fit(
                "[bold green]VicAlerts[/bold green]\n"
                f"Polling every {self.interval} seconds\n"
                "Press Ctrl+C to stop",
                border_style="green",
            )
        )

        self.running = True

        with Live(console=console, refresh_per_second=2) as live:
            try:
                while self.running:
                    # Run poll
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    live.update(f"[dim]{timestamp}[/dim] - Polling...")

                    try:
                        changes = self.run_once()
                    except Exception as e:
                        console.print(f"[red]Poll failed: {e}")
                        changes = False

                    # Countdown to next poll
                    for remaining in range(self.interval, 0, -1):
                        if not self.running:
                            break

                        status = (
                            "[green]Changes detected[/green]"
                            if changes
                            else "No changes"
                        )
                        live.update(
                            f"[dim]{timestamp}[/dim] - {status}\n"
                            f"Next poll in {remaining}s..."
                        )
                        time.sleep(1)

            except KeyboardInterrupt:
                pass

        console.print("\n[green]Poller stopped.")
