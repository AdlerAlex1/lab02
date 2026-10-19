

from collections import Counter


def new_stats():
    # Создать пустую статистику — обычный словарь.
    return {
        "total": 0,
        "by_level": Counter(),
        "by_source": Counter(),
        "errors_by_source": Counter(),
        "first_ts": None,
        "last_ts": None,
        "skipped": 0,
    }


def add(stats, ev):
    # Обновить статистику одним событием
    # ev — кортеж (timestamp, level, source, message)
    ts, level, source, _message = ev
    stats["total"] += 1
    stats["by_level"][level] += 1
    stats["by_source"][source] += 1

    if level in ("ERROR", "CRITICAL"):
        stats["errors_by_source"][source] += 1

    if stats["first_ts"] is None or ts < stats["first_ts"]:
        stats["first_ts"] = ts
    if stats["last_ts"] is None or ts > stats["last_ts"]:
        stats["last_ts"] = ts


def merge(a, b):
    # Слить статистику b в a (a меняется, b — нет)
    a["total"] += b["total"]
    a["by_level"].update(b["by_level"])
    a["by_source"].update(b["by_source"])
    a["errors_by_source"].update(b["errors_by_source"])
    a["skipped"] += b["skipped"]

    if b["first_ts"] is not None and (
        a["first_ts"] is None or b["first_ts"] < a["first_ts"]
    ):
        a["first_ts"] = b["first_ts"]
    if b["last_ts"] is not None and (
        a["last_ts"] is None or b["last_ts"] > a["last_ts"]
    ):
        a["last_ts"] = b["last_ts"]


def collect(events, stats):
    # Прогнать поток событий через stats
    for ev in events:
        if ev is None:
            stats["skipped"] += 1
        else:
            add(stats, ev)