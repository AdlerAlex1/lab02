

import argparse
import logging
import sys
from pathlib import Path

from .analysis import collect, new_stats
from .errors import InvalidEventError
from .parsers import iter_csv, iter_jsonl
from .report import build_report, write_report


def build_parser():
    # Собрать парсер аргументов командной строки.
    p = argparse.ArgumentParser(
        prog="streamstats",
        description="Потоковый анализатор логов: строит статистику по CSV и JSONL.",
    )
    sub = p.add_subparsers(dest="cmd", required=True, metavar="КОМАНДА")

    a = sub.add_parser(
        "analyze",
        help="Проанализировать файлы и записать JSON-отчёт",
        description="Прочитать один или несколько файлов логов и записать отчёт в JSON.",
    )
    a.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        metavar="ВХОД",
        help="Один или несколько файлов логов",
    )
    a.add_argument(
        "--format",
        choices=("csv", "jsonl"),
        required=True,
        help="Формат входных файлов: csv или jsonl",
    )
    a.add_argument(
        "--output",
        type=Path,
        required=True,
        metavar="ОТЧЁТ",
        help="Путь к выходному JSON-отчёту",
    )
    a.add_argument(
        "--skip-invalid",
        action="store_true",
        help="Пропускать битые строки вместо остановки",
    )
    return p


def run_analyze(args):
    # Выбор парсера по --format.
    if args.format == "csv":
        parser = iter_csv
    elif args.format == "jsonl":
        parser = iter_jsonl
    else:
        print(f"ошибка: неподдерживаемый формат {args.format}", file=sys.stderr)
        return 2

    # Один общий stats-словарь на все файлы — всё суммируется.
    total = new_stats()

    for path in args.inputs:
        if not path.is_file():
            print(f"ошибка: файл не найден: {path}", file=sys.stderr)
            return 2
        try:
            # skip_invalid передаётся В ПАРСЕР: политика
            collect(parser(path, skip_invalid=args.skip_invalid), total)
        except InvalidEventError as exc:
            # Ловим ТОЛЬКО InvalidEventError. Всё остальное пусть летит наружу
            print(
                f"ошибка: битое событие в {exc.file}:{exc.line_no}: {exc}",
                file=sys.stderr,
            )
            return 2

    write_report(build_report(total), args.output)
    return 0


def main(argv=None):
    # Настраиваем логирование один раз: WARNING и выше в stderr
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_analyze(args)


if __name__ == "__main__":
    sys.exit(main())