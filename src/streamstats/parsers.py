

import csv
import json
import logging
from datetime import datetime
from pathlib import Path

from .errors import InvalidEventError, InvalidTimestampError

log = logging.getLogger(__name__)


REQUIRED_FIELDS = ("timestamp", "level", "source", "message")


VALID_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def _build_event(row, file, line_no):
    # Проверить словарь и вернуть кортеж события.
    # Событие - кортеж

    # Все обязательные поля есть и непусты(проверка)
    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or str(value).strip() == "":
            raise InvalidEventError(
                f"отсутствует поле {field!r}",
                file=file, line_no=line_no,
            )

    # уровень - из списка допустимых?
    level = str(row["level"]).strip()
    if level not in VALID_LEVELS:
        raise InvalidEventError(
            f"неизвестный уровень {level!r}",
            file=file, line_no=line_no,
        )

    #Timestamp парсится?
    try:
        ts = datetime.fromisoformat(
            str(row["timestamp"]).replace("Z", "+00:00")
        )
    except ValueError:
        raise InvalidTimestampError(
            f"неверная временная метка: {row['timestamp']!r}",
            file=file, line_no=line_no,
        )

    # Собираем событие в кортеж.Порядок фиксирован!
    return (ts, level, str(row["source"]).strip(), str(row["message"]))


def iter_csv(path: Path, skip_invalid: bool = False):
    # Генератор событий из csv-файла с заголовком
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return

        # enumerate(reader, start=2): 1-я строка файла — заголовок,
        # поэтому первая строка данных идёт под номером 2.
        for line_no, row in enumerate(reader, start=2):
            try:
                # try/except вокруг yield: _build_event вызывается ДО
                # отдачи значения поэтому исключение ловится здесь
                yield _build_event(row, str(path), line_no)
            except InvalidEventError as exc:
                if not skip_invalid:
                    # Строгий режим — пробрасываем наверх.
                    raise
                # --skip-invalid: пишем WARNING и отдаём None —
                log.warning(
                    "пропущено %s:%d: %s", exc.file, exc.line_no, exc
                )
                yield None


def iter_jsonl(path: Path, skip_invalid: bool = False):
    # Генератор событий из jsonl 
    with path.open("r", encoding="utf-8") as f:
        # for line in f — построчное чтение, без readlines().
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            #Парсим JSON
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                exc = InvalidEventError(
                    "некорректный JSON",
                    file=str(path), line_no=line_no, raw=line,
                )
                if not skip_invalid:
                    raise exc
                log.warning(
                    "пропущено %s:%d: %s", exc.file, exc.line_no, exc
                )
                yield None
                continue

            #Строка JSONL должна быть объектом
            if not isinstance(obj, dict):
                exc = InvalidEventError(
                    "строка JSONL не является объектом",
                    file=str(path), line_no=line_no, raw=line,
                )
                if not skip_invalid:
                    raise exc
                log.warning(
                    "пропущено %s:%d: %s", exc.file, exc.line_no, exc
                )
                yield None
                continue

            #Проверяем поля и отдаём событие
            try:
                yield _build_event(obj, str(path), line_no)
            except InvalidEventError as exc:
                if not skip_invalid:
                    raise
                log.warning(
                    "пропущено %s:%d: %s", exc.file, exc.line_no, exc
                )
                yield None