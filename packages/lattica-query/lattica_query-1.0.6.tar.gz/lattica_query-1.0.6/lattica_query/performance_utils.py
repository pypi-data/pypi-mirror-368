import json
from typing import List, Tuple
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parse_server_timing_line(header: str) -> List[Tuple[str, float]]:
    """
    Parses a single Server-Timing string and returns exclusive durations.
    Assumes each part includes the next one.
    """
    parts = []
    for token in header.split(','):
        token = token.strip()
        if ';dur=' in token:
            name, dur = token.split(';dur=')
            try:
                parts.append((name.strip(), float(dur) / 1000))  # Convert ms to seconds
            except ValueError:
                continue

    # Compute exclusive durations
    exclusive = []
    for i in range(len(parts) - 1):
        name, dur = parts[i]
        next_dur = parts[i + 1][1]
        exclusive.append((name, round(dur - next_dur, 2)))
    if parts:
        name, dur = parts[-1]
        exclusive.append((name, round(dur, 2)))
    return exclusive


def _summarize_timing(data: List[Tuple[str, float]],  src: str):
    totals = defaultdict(float)
    for key, value in data:
        totals[key] += value

    grand_total = sum(totals.values())

    sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    breakdown = [
        {
            "step": name,
            "duration_sec": round(dur, 3),
            "percent": round((dur / grand_total * 100), 1)
        }
        for name, dur in sorted_totals
    ]

    log_payload = {
        "event": "timing_summary",
        "source": src,
        "total_time_sec": round(grand_total, 3),
        "breakdown": breakdown
    }

    logger.info(json.dumps(log_payload, indent=4))


def log_timing_breakdown(header_strings_msec: List[str], client_time_sec: List[Tuple[str, float]]):
    """
    Aggregates and prints exclusive durations from a list of Server-Timing header strings.
    """
    be_time_sec = [word for line in header_strings_msec for word in _parse_server_timing_line(line)]
    _summarize_timing(be_time_sec, "BE")

    _summarize_timing(client_time_sec, "CLIENT")
