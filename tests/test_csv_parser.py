from datetime import datetime, timezone

import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.parsers import iter_csv


# события, поля и timestamp разобраны правильно
def test_csv_ok(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,api,start\n"
        "2024-01-01T10:00:05Z,ERROR,db,fail\n",
        encoding="utf-8",
    )
    events = list(iter_csv(p))
    assert len(events) == 2
    _ts0, level0, source0, _msg0 = events[0]
    ts1, level1, _source1, _msg1 = events[1]
    assert source0 == "api"
    assert level0 == "INFO"
    assert level1 == "ERROR"
    assert ts1 == datetime(2024, 1, 1, 10, 0, 5, tzinfo=timezone.utc)

# проверка на пустоту(0 событий)
def test_csv_empty(tmp_path):
    p = tmp_path / "e.csv"
    p.write_text("timestamp,level,source,message\n", encoding="utf-8")
    assert list(iter_csv(p)) == []

#пустой source
def test_csv_missing_field(tmp_path):
    p = tmp_path / "m.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,,x\n",
        encoding="utf-8",
    )
    with pytest.raises(InvalidEventError) as ei:
        list(iter_csv(p))
    assert "source" in str(ei.value)

# битое время
def test_csv_bad_timestamp(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "NOT-A-DATE,INFO,api,x\n",
        encoding="utf-8",
    )
    with pytest.raises(InvalidTimestampError) as ei:
        list(iter_csv(p))
    assert ei.value.line_no == 2

# проверка на русский язык
def test_csv_unicode(tmp_path):
    p = tmp_path / "u.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,сервер-1,запуск\n",
        encoding="utf-8",
    )
    events = list(iter_csv(p))
    _ts, _level, source, message = events[0]
    assert source == "сервер-1"
    assert message == "запуск"