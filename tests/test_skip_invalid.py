import pytest

from streamstats.analysis import collect, new_stats
from streamstats.errors import InvalidEventError
from streamstats.parsers import iter_csv, iter_jsonl


#строгий режим битый уровень
def test_strict_mode_raises(tmp_path):
    p = tmp_path / "b.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,MAYBE,api,x\n",
        encoding="utf-8",
    )
    with pytest.raises(InvalidEventError):
        list(iter_csv(p, skip_invalid=False))

# на месте одной строки MAYBE (None)
def test_skip_invalid_yields_none(tmp_path):
    p = tmp_path / "b.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,api,x\n"
        "2024-01-01T10:00:05Z,MAYBE,db,y\n"
        "2024-01-01T10:00:07Z,INFO,api,z\n",
        encoding="utf-8",
    )
    items = list(iter_csv(p, skip_invalid=True))
    assert len(items) == 3
    assert items[1] is None

# total - валидные skipped - битые
def test_skip_invalid_stats(tmp_path):
    p = tmp_path / "b.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,api,x\n"
        "2024-01-01T10:00:05Z,MAYBE,db,y\n",
        encoding="utf-8",
    )
    stats = new_stats()
    collect(iter_csv(p, skip_invalid=True), stats)
    assert stats["total"] == 1
    assert stats["skipped"] == 1

# проверка на jsonl
def test_skip_invalid_jsonl(tmp_path):
    p = tmp_path / "b.jsonl"
    p.write_text(
        '{"timestamp":"2024-01-01T10:00:00Z","level":"INFO","source":"s","message":"ok"}\n'
        'garbage\n',
        encoding="utf-8",
    )
    stats = new_stats()
    collect(iter_jsonl(p, skip_invalid=True), stats)
    assert stats["total"] == 1
    assert stats["skipped"] == 1