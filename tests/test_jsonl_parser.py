import pytest

from streamstats.errors import InvalidEventError
from streamstats.parsers import iter_jsonl


# проверка 2 события разобраны правильно
def test_jsonl_ok(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text(
        '{"timestamp":"2024-01-01T10:00:00Z","level":"INFO","source":"api","message":"x"}\n'
        '{"timestamp":"2024-01-01T10:00:05Z","level":"ERROR","source":"db","message":"y"}\n',
        encoding="utf-8",
    )
    events = list(iter_jsonl(p))
    assert len(events) == 2
    _ts, _level, source, _message = events[1]
    assert source == "db"

# 0 событий
def test_jsonl_empty(tmp_path):
    p = tmp_path / "e.jsonl"
    p.write_text("", encoding="utf-8")
    assert list(iter_jsonl(p)) == []

# битый json
def test_jsonl_bad_json(tmp_path):
    p = tmp_path / "b.jsonl"
    p.write_text("not json\n", encoding="utf-8")
    with pytest.raises(InvalidEventError) as ei:
        list(iter_jsonl(p))
    assert ei.value.line_no == 1

# строка число (не обьект)
def test_jsonl_not_object(tmp_path):
    p = tmp_path / "n.jsonl"
    p.write_text("42\n", encoding="utf-8")
    with pytest.raises(InvalidEventError):
        list(iter_jsonl(p))
