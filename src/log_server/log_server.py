#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""x_logger が保存したログを公開する gRPC ログサーバー。

デバイス用途では XLogger の logger_name を logical log ID として扱い、
標準の保存配置を次のようにする。

    <log_prefix>/<logger_name>/<logger_name>.log
    <log_prefix>/<logger_name>/<logger_name>.log.YYYY-MM-DD

現在ログは file / rotating のどちらでも参照できる。
日付指定ログは TimedRotatingFileHandler(when="midnight") の履歴を扱う。
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, List, Optional, Sequence, Tuple, Union


class LogController:
    """短い応答を扱う LogServer の通常 RPC コントローラ。"""

    def __init__(
        self,
        log_prefix: Union[str, Path],
        log_suffix: str = ".log",
        encoding: str = "utf-8",
    ) -> None:
        self._log_prefix = Path(log_prefix).expanduser().resolve()
        self._log_suffix = str(log_suffix)
        self._encoding = str(encoding)

        if not self._log_prefix.is_dir():
            raise NotADirectoryError(
                f"log prefix does not exist: {self._log_prefix}"
            )

    def tail(
        self,
        logger_name: str,
        lines: int = 100,
        date: Optional[str] = None,
    ) -> str:
        """現在または指定日のログ末尾を返す。"""
        if isinstance(lines, bool) or not isinstance(lines, int) or lines <= 0:
            raise ValueError("lines must be a positive integer")

        path = self._resolve_log_path(logger_name, date)
        return self._tail_file(path, lines)

    def dates(self, logger_name: str) -> List[str]:
        """取得可能なローテーション済みログの日付を返す。"""
        log_dir = self._logger_dir(logger_name)
        base_name = self._base_name(logger_name)
        prefix = f"{base_name}."
        found = []

        if not log_dir.is_dir():
            return found

        for path in log_dir.glob(f"{base_name}.*"):
            suffix = path.name[len(prefix):]
            if self._is_date_string(suffix):
                found.append(suffix)

        return sorted(found, reverse=True)

    def exists(
        self,
        logger_name: str,
        date: Optional[str] = None,
    ) -> bool:
        """現在または指定日のログが存在するか返す。"""
        try:
            path = self._resolve_log_path(
                logger_name,
                date,
                require_exists=False,
            )
        except (TypeError, ValueError):
            return False
        return path.is_file()

    def _validate_logger_name(self, logger_name: str) -> str:
        if not isinstance(logger_name, str) or not logger_name:
            raise ValueError("logger_name must be a non-empty string")
        if Path(logger_name).name != logger_name:
            raise ValueError("logger_name must not contain a path")
        if logger_name in (".", ".."):
            raise ValueError("logger_name must not contain a path")
        return logger_name

    def _logger_dir(self, logger_name: str) -> Path:
        name = self._validate_logger_name(logger_name)
        return self._log_prefix / name

    def _base_name(self, logger_name: str) -> str:
        name = self._validate_logger_name(logger_name)
        return f"{name}{self._log_suffix}"

    def _resolve_log_path(
        self,
        logger_name: str,
        date_value: Optional[str],
        require_exists: bool = True,
    ) -> Path:
        log_dir = self._logger_dir(logger_name)
        base_name = self._base_name(logger_name)

        if date_value is None:
            path = log_dir / base_name
        else:
            self._validate_date(date_value)
            path = log_dir / f"{base_name}.{date_value}"

        if require_exists and not path.is_file():
            raise FileNotFoundError(f"log file does not exist: {path}")
        return path

    @staticmethod
    def _validate_date(value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("date must be a string in YYYY-MM-DD format")
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format")
        if parsed.strftime("%Y-%m-%d") != value:
            raise ValueError("date must be in YYYY-MM-DD format")

    @staticmethod
    def _is_date_string(value: str) -> bool:
        try:
            LogController._validate_date(value)
        except (TypeError, ValueError):
            return False
        return True

    def _tail_file(self, path: Path, lines: int) -> str:
        block_size = 8192
        data = b""

        with path.open("rb") as file_obj:
            file_obj.seek(0, 2)
            position = file_obj.tell()

            while position > 0 and data.count(b"\n") <= lines:
                read_size = min(block_size, position)
                position -= read_size
                file_obj.seek(position)
                data = file_obj.read(read_size) + data

        text = data.decode(self._encoding)
        return "".join(text.splitlines(keepends=True)[-lines:])


class LogStream:
    """大きなログ本文を server-streaming で返す。"""

    def __init__(
        self,
        controller: LogController,
        chunk_size: int = 256 * 1024,
    ) -> None:
        if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
            raise ValueError("chunk_size must be a positive integer")
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        self._controller = controller
        self._chunk_size = chunk_size

    def read(
        self,
        logger_name: str,
        date: Optional[str] = None,
    ) -> Iterator[str]:
        """ログ全文を文字列チャンクとして順次返す。"""
        path = self._controller._resolve_log_path(logger_name, date)
        with path.open(
            "r",
            encoding=self._controller._encoding,
            errors="strict",
        ) as file_obj:
            while True:
                chunk = file_obj.read(self._chunk_size)
                if not chunk:
                    break
                yield chunk


def create_log_grpc_server(
    log_prefix: Union[str, Path],
    log_suffix: str = ".log",
    encoding: str = "utf-8",
    chunk_size: int = 256 * 1024,
    max_workers: int = 10,
    logger: Optional[Any] = None,
    log_level: Optional[str] = None,
    grpc_options: Optional[Sequence[Tuple[str, Any]]] = None,
):
    """LogController/LogStream を載せた grpc_frame server を生成する。"""
    from grpc_frame.grpc_server import create_grpc_server

    controller = LogController(
        log_prefix=log_prefix,
        log_suffix=log_suffix,
        encoding=encoding,
    )
    stream = LogStream(controller=controller, chunk_size=chunk_size)

    return create_grpc_server(
        ctrl_obj=controller,
        stream_obj=stream,
        max_workers=max_workers,
        logger=logger,
        log_level=log_level,
        grpc_options=grpc_options,
    )
