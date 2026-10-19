

import json
from pathlib import Path


def build_report(stats):
    top_errors = stats["errors_by_source"].most_common(5)
    return {
        "total_events": stats["total"],
        "skipped_lines": stats["skipped"],
        "by_level": dict(stats["by_level"]),
        "by_source": dict(stats["by_source"]),
        "top_error_sources": [
            {"source": s, "count": c} for s, c in top_errors
        ],
        "first_timestamp": (
            stats["first_ts"].isoformat() if stats["first_ts"] else None
        ),
        "last_timestamp": (
            stats["last_ts"].isoformat() if stats["last_ts"] else None
        ),
    }


def write_report(report, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)