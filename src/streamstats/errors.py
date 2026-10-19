

from __future__ import annotations


class StreamStatsError(Exception):
    """Базовое исключение пакета."""


class UnsupportedFormatError(StreamStatsError):
    """Формат не поддерживается."""


class InvalidEventError(StreamStatsError):
    """Строка не является корректным событием."""

    def __init__(
        self,
        message: str,
        *,
        file: str = "<unknown>",
        line_no: int = 0,
        raw: str = "",
    ) -> None:
        super().__init__(message)
        self.file = file
        self.line_no = line_no
        self.raw = raw


class InvalidTimestampError(InvalidEventError):
    """Timestamp не парсится."""


class CLIConfigError(StreamStatsError):
    """Ошибка в аргументах CLI."""