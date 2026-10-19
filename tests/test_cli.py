import json

from streamstats.__main__ import main


def test_cli_ok(tmp_path):
    #cli: успешный прогон, код 0, отчёт создан и правильный
    src = tmp_path / "in.csv"
    src.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,api,x\n"
        "2024-01-01T10:00:05Z,ERROR,db,y\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.json"
    code = main(["analyze", str(src), "--format", "csv", "--output", str(out)])
    assert code == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total_events"] == 2
    assert report["top_error_sources"] == [{"source": "db", "count": 1}]


def test_cli_invalid_exit_2(tmp_path):
    #CLI строгий: битая строка - код 2, файл не создан.
    src = tmp_path / "bad.csv"
    src.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,MAYBE,api,x\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.json"
    code = main(["analyze", str(src), "--format", "csv", "--output", str(out)])
    assert code == 2
    assert not out.exists()


def test_cli_skip_invalid(tmp_path):
    #cli --skip-invalid: код 0, skipped_lines в отчёте
    src = tmp_path / "bad.csv"
    src.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,api,x\n"
        "2024-01-01T10:00:05Z,MAYBE,db,y\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.json"
    code = main([
        "analyze", str(src), "--format", "csv",
        "--output", str(out), "--skip-invalid",
    ])
    assert code == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total_events"] == 1
    assert report["skipped_lines"] == 1


def test_cli_missing_file(tmp_path):
    #Cli: файла нет - код 2, файл отчёта не создан
    out = tmp_path / "out.json"
    code = main([
        "analyze", str(tmp_path / "nope.csv"),
        "--format", "csv", "--output", str(out),
    ])
    assert code == 2
    assert not out.exists()