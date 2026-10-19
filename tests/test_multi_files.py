from streamstats.analysis import collect, merge, new_stats
from streamstats.parsers import iter_csv


# 2 файла в один
def test_two_files(tmp_path):
    a = tmp_path / "a.csv"
    a.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,api,x\n",
        encoding="utf-8",
    )
    b = tmp_path / "b.csv"
    b.write_text(
        "timestamp,level,source,message\n"
        "2024-01-02T10:00:00Z,ERROR,db,y\n",
        encoding="utf-8",
    )
    stats = new_stats()
    collect(iter_csv(a), stats)
    collect(iter_csv(b), stats)
    assert stats["total"] == 2
    assert stats["by_source"]["api"] == 1
    assert stats["by_source"]["db"] == 1
    assert stats["first_ts"].day == 1
    assert stats["last_ts"].day == 2

# stats + merge
def test_merge(tmp_path):
    a = tmp_path / "a.csv"
    a.write_text(
        "timestamp,level,source,message\n"
        "2024-01-01T10:00:00Z,INFO,api,x\n",
        encoding="utf-8",
    )
    b = tmp_path / "b.csv"
    b.write_text(
        "timestamp,level,source,message\n"
        "2024-01-02T09:00:00Z,ERROR,db,y\n",
        encoding="utf-8",
    )
    sa = new_stats()
    collect(iter_csv(a), sa)
    sb = new_stats()
    collect(iter_csv(b), sb)
    merge(sa, sb)
    assert sa["total"] == 2
    assert sa["by_level"]["INFO"] == 1
    assert sa["by_level"]["ERROR"] == 1