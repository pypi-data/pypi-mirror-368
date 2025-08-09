#!/usr/bin/env python3
"""
get-trace-id  – Generate a file-safe, timezone-normalized Trace ID.

• Default timezone: UTC to ensure consistent IDs across environments.
• Optional --timezone / -t flag lets you pick any IANA zone, e.g. "America/New_York" or "Europe/London".
"""

from datetime import datetime
import argparse

try:
    from zoneinfo import ZoneInfo  # Python ≥3.9
except ImportError:  # Python 3.7–3.8
    from backports.zoneinfo import ZoneInfo  # pip install backports.zoneinfo


def generate_trace_id(tz_name: str = "UTC") -> str:
    """Return a Trace ID like 20250721T162218+0000 for the given timezone."""
    tz = ZoneInfo(tz_name)
    now = datetime.now(ZoneInfo("UTC")).astimezone(tz)
    # %z gives ±HHMM without a colon – exactly what the Grit Labs spec needs
    return now.strftime("%Y%m%dT%H%M%S%z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Trace ID.")
    parser.add_argument(
        "-t",
        "--timezone",
        default="UTC",
        help="IANA timezone name (default: UTC).",
    )
    args = parser.parse_args()
    try:
        trace_id = generate_trace_id(args.timezone)
    except Exception as exc:
        parser.error(f"Invalid timezone '{args.timezone}': {exc}")
    print(trace_id)


if __name__ == "__main__":
    main()
