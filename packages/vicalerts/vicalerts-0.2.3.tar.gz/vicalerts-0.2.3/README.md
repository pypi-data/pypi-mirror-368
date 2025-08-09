# VicAlerts

Track and archive VicEmergency incidents to a local SQLite database.

## Purpose

VicAlerts polls the public VicEmergency GeoJSON feed, stores every version of every event, and exposes a small CLI for querying the result. Useful for incident timelines, post-event analysis, or keeping your own history for when events expire from the feed. It is designed to run 24/7 to collect data.

## Installation

```bash
uv pip install vicalerts
```

Requires Python 3.10 or newer.

## Quick start

```bash
# Continuous polling (60 s default)
vicalerts run

# One-off fetch (handy in cron)
vicalerts run --once
```

## CLI reference

| Command              | Description                          | Key options                                                                                                                            |
| -------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `run`                | Poll feed and write to the DB        | `--once`, `--interval <seconds>` (>=10), `--db <path>`, `--no-progress`                                                                |
| `events`             | List events (active only by default) | `--all`, `--type incident\|warning`, `--status <text>`, `--category <text>`, `--limit <n>`, `--format table\|json\|csv`, `--db <path>` |
| `history <EVENT_ID>` | Show full version history            | `--db <path>`                                                                                                                          |
| `stats`              | Print DB totals                      | `--db <path>`                                                                                                                          |

All commands accept `--help`.

## Defaults

| Setting      | Value                                                                                                              |
| ------------ | ------------------------------------------------------------------------------------------------------------------ |
| Feed URL     | [https://emergency.vic.gov.au/public/events-geojson.json](https://emergency.vic.gov.au/public/events-geojson.json) |
| Interval     | 60 s                                                                                                               |
| HTTP timeout | 30 s                                                                                                               |
| Retries      | 3 (1 s, then 2 s, then 4 s)                                                                                        |
| Database     | `./vicalerts.sqlite`                                                                                               |

## Example workflows

```bash
# 1. Nightly stats
vicalerts stats --db /data/vic.sqlite

# 2. Export active incidents as JSON
vicalerts events --type incident --format json > incidents.json

# 3. Inspect how an event evolved
vicalerts history 123456 --db /data/vic.sqlite
```

## Notes and limitations

* Disk growth is roughly 10–20 MB per month (feeds are compressed).
* Memory use is modest (< 50 MB typical).
* Geometry is reduced to centroids; polygons are not preserved.
* Tested on Linux and macOS; Windows untested.
* 60s interval is based on VicEmergency website; impact is no different to having the site open.

## Attribution

Data © State of Victoria (EMV) - data licensed under CC BY 4.0 AU
