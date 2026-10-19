# streamstats — потоковый анализатор файлов

Читает логи в формате CSV или JSONL построчно и строит статистический отчёт в JSON:
общее число событий, разбивка по уровням и источникам, топ-5 источников ошибок,
первая и последняя метки времени.(ПРЯМОЙ И ОТНОСИТЕЛЬНЫЙ ПУТЬ!)

## Структура проекта

    lab_02/
      pyproject.toml            конфигурация пакета и pytest
      README.md                 
      src/
        streamstats/
          __init__.py           
          __main__.py           CLI
          errors.py             иерархия исключений
          parsers.py            построчные парсеры CSV и JSONL
          analysis.py           Stats и функция collect
          report.py             сборка и запись JSON-отчёта
      tests/
        test_csv_parser.py      unit-тесты парсера CSV
        test_jsonl_parser.py    unit-тесты парсера JSONL
        test_skip_invalid.py    тесты строгого режима и --skip-invalid
        test_multiple_files.py  тесты объединения файлов
        test_cli.py             integration-тесты CLI
      data/                     файлы для проверки
      a.csv                     валидный csv
      b.jsonl                   валидный jsonl
      a_inv.csv                 невалид csv
      b_inv.jsonl               невалид jsonl            

## Установка

    git clone https://github.com/AdlerAlex1/lab02.git
    cd ../lab02
    python -m pip install -e . / python3 -m pip install -e .

## Запуск

    python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl --output REPORT.json

Примеры:

    python -m streamstats analyze data/a.csv --format csv --output report.json
    python -m streamstats analyze data/a.jsonl --format jsonl --output report.json
    python -m streamstats analyze data/a.csv data/b.csv --format csv --output report.json

Пропускать битые строки вместо остановки:

    python -m streamstats analyze data/a.jsonl --format jsonl --output report.json --skip-invalid

## Форматы входных данных

### CSV

Первая строка — заголовок с обязательными полями `timestamp`, `level`, `source`, `message`.

    timestamp,level,source,message
    2024-01-01T10:00:00Z,INFO,api,started
    2024-01-01T10:00:05Z,ERROR,db,connection failed

### JSONL

Одна строка — один JSON-объект с теми же полями.

    {"timestamp":"2024-01-01T10:00:00Z","level":"INFO","source":"api","message":"started"}
    {"timestamp":"2024-01-01T10:00:05Z","level":"ERROR","source":"db","message":"connection failed"}

Обязательные поля:

- `timestamp` 
- `level` — одно из `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`;
- `source` — непустая строка;
- `message` — строка.

## Режимы обработки ошибок

- По умолчанию: первая же битая строка останавливает обработку. В stderr
  выводится файл и номер строки, код возврата — `2`.
- С `--skip-invalid`: битая строка пропускается, в лог пишется WARNING,
  в отчёте увеличивается поле `skipped_lines`, код возврата — `0`.

## Отчёт

По умолчанию пишется в файл, указанный в `--output`. Пример:

    {
      "total_events": 3,
      "skipped_lines": 0,
      "by_level": {"INFO": 2, "ERROR": 1},
      "by_source": {"api": 2, "db": 1},
      "top_error_sources": [{"source": "db", "count": 1}],
      "first_timestamp": "2024-01-01T10:00:00+00:00",
      "last_timestamp": "2024-01-01T10:00:05+00:00"
    }

## Проверка

    python -m pytest
    ruff check .
    python -m streamstats --help
