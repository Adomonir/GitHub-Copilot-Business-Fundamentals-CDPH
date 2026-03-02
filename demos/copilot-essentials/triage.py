#!/usr/bin/env python3
"""
Quick log triage utility
────────────────────────
  • Accepts   *.log  or  *.log.gz
  • Filters   last N minutes (sliding window)
  • Tallies   (status‑code, endpoint) pairs
  • Optional  --status 499,321 for focused searching

  A noisy incident page reveals a spike in 321 or 499 errors, but the observability stack is lagging. You need a quick, local log sweep to spot patterns and counts.
"""

from pathlib import Path
from datetime import datetime, timedelta, timezone
import argparse
import gzip
import re
import sys
from collections import Counter
from typing import Iterable, Tuple

# ---------------------------------------------------------------------------
# ✨ Function placeholders – let Copilot write the bodies ✨
# ---------------------------------------------------------------------------

def read_lines(file_path: Path) -> Iterable[str]:
    """Open plain or gzipped log file and yield each line (stripped)."""
    if file_path.suffix == ".gz":
        with gzip.open(file_path, "rt", encoding="utf-8") as f:
            for line in f:
                yield line.strip()
    else:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    yield line.strip()
    pass  # ← Copilot will fill this in



def parse_line(line: str) -> Tuple[datetime, int, str] | None:
    """Return (timestamp_utc, status_code_int, url_path) or None if malformed."""
    # Example regex for common/combined log format
    log_pattern = re.compile(
        r'^\S+ \S+ \S+ \[(?P<timestamp>[^\]]+)\] "\S+ (?P<path>\S+) \S+" (?P<status>\d{3})'
    )
    match = log_pattern.match(line)
    if not match:
        return None
    timestamp_str = match.group("timestamp")
    path = match.group("path")
    status = int(match.group("status"))
    # Convert timestamp to UTC datetime
    timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
    timestamp_utc = timestamp.astimezone(timezone.utc)
    return timestamp_utc, status, path

    pass  # ← Copilot will fill this in


def triage(
    lines: Iterable[str],
    minutes: int,
    wanted_status: set[int] | None
) -> Counter[Tuple[int, str]]:
    """Aggregate counts for lines within the window and matching status filter."""
    now_utc = datetime.now(timezone.utc)
    cutoff_utc = now_utc - timedelta(minutes=minutes)
    counter: Counter[Tuple[int, str]] = Counter()
    for line in lines:
        parsed = parse_line(line)
        if not parsed:
            continue  # Skip malformed lines
        timestamp_utc, status, path = parsed
        if timestamp_utc < cutoff_utc:
            continue  # Skip old entries
        if wanted_status and status not in wanted_status:
            continue  # Skip unwanted status codes
        counter[(status, path)] += 1
    return counter


def render(counter: Counter[Tuple[int, str]], top: int) -> None:
    """Pretty‑print a Markdown‑style table of the top offenders."""
    print("| # | Status | Path | Hits |")
    print("|---:|---:|---|---:|")
    for i, ((status, path), hits) in enumerate(counter.most_common(top), start=1):
        print(f"| {i} | {status} | {path} | {hits} |")
        

    pass  # ← Copilot will fill this in



def main() -> int:
    """Wire everything together with argparse CLI options."""
    parser = argparse.ArgumentParser(description="Triage recent endpoint failures from logs.")
    parser.add_argument("file", help="Path to .log or .log.gz file")
    parser.add_argument("--minutes", type=int, default=15, help="Lookback window in minutes (default: 15)")
    parser.add_argument("--status", default="", help='Comma-separated statuses, e.g. "499,321"')
    parser.add_argument("--top", type=int, default=10, help="Top N rows to print (default: 10)")
    args = parser.parse_args()

    if args.minutes <= 0:
        parser.error("--minutes must be > 0")
    if args.top <= 0:
        parser.error("--top must be > 0")

    statuses = None
    if args.status.strip():
        try:
            statuses = {int(s.strip()) for s in args.status.split(",") if s.strip()}
        except ValueError:
            parser.error('--status must be comma-separated integers, e.g. "499,321"')

    file_path = Path(args.file)
    if not file_path.exists():
        parser.error(f"File not found: {args.file}")

    # Read lines from file and triage them
    lines = read_lines(file_path)
    counter = triage(
        lines=lines,
        minutes=args.minutes,
        wanted_status=statuses,
    )

    if not counter:
        print("No matching log entries found.")
        return 0

    render(counter, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
