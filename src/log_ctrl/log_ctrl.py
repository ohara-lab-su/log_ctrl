#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union


class LogCtrl:
    """ログディレクトリをローカルで扱う制御クラス。"""

    def __init__(
        self,
        log_dir: Union[str, Path],
        encoding: str = "utf-8",
    ) -> None:
        self._log_dir = Path(log_dir).expanduser().resolve()
        self._encoding = str(encoding)

        if not self._log_dir.is_dir():
            raise NotADirectoryError(
                "log directory does not exist: " + str(self._log_dir)
            )

    def log_names(self) -> List[str]:
        """実在する *.log / *.log.YYYY-MM-DD から log_name 一覧を返す。"""
        names = set()

        for path in self._log_dir.iterdir():
            if not path.is_file():
                continue

            parsed = self._parse_log_filename(path.name)
            if parsed is None:
                continue

            log_name, _date_value = parsed
            names.add(log_name)

        return sorted(names)

    def dates(
        self,
        log_name: str,
    ) -> List[str]:
        """指定 log_name に実在するローテーション済み日付一覧を返す。"""
        name = self._validate_log_name(log_name)
        prefix = name + ".log."
        values = set()

        for path in self._log_dir.iterdir():
            if not path.is_file():
                continue

            if not path.name.startswith(prefix):
                continue

            date_value = path.name[len(prefix):]

            if self._is_date(date_value):
                values.add(date_value)

        return sorted(values, reverse=True)

    def raw_files(self) -> List[str]:
        """トラブル調査用に log_dir 以下の全ファイル相対パスをそのまま返す。"""
        files = []

        for path in self._log_dir.rglob("*"):
            if not path.is_file():
                continue

            files.append(
                path.relative_to(self._log_dir).as_posix()
            )

        return sorted(files)

    def _resolve_raw_path(
        self,
        relative_path: str,
    ) -> Path:
        if not isinstance(relative_path, str):
            raise ValueError("relative_path must be a non-empty string")

        if relative_path == "":
            raise ValueError("relative_path must be a non-empty string")

        relative = Path(relative_path)

        if relative.is_absolute():
            raise ValueError("relative_path must be relative to log_dir")

        path = (self._log_dir / relative).resolve()

        try:
            path.relative_to(self._log_dir)
        except ValueError:
            raise ValueError("relative_path must stay inside log_dir")

        if not path.is_file():
            raise FileNotFoundError(
                "file does not exist: " + str(path)
            )

        return path

    def exists(
        self,
        log_name: str,
        date: Optional[str] = None,
    ) -> bool:
        """指定した現在ログまたは日付ログが実在するか返す。"""
        try:
            path = self._resolve_log_path(
                log_name,
                date,
                require_exists=False,
            )
        except (TypeError, ValueError):
            return False

        return path.is_file()

    def tail(
        self,
        log_name: str,
        lines: int = 100,
        date: Optional[str] = None,
    ) -> str:
        """指定ログの末尾を文字列で返す。"""
        if isinstance(lines, bool):
            raise ValueError("lines must be a positive integer")

        if not isinstance(lines, int):
            raise ValueError("lines must be a positive integer")

        if lines <= 0:
            raise ValueError("lines must be a positive integer")

        path = self._resolve_log_path(log_name, date)
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

    def _resolve_log_path(
        self,
        log_name: str,
        date: Optional[str] = None,
        require_exists: bool = True,
    ) -> Path:
        name = self._validate_log_name(log_name)

        if date is None:
            filename = name + ".log"
        else:
            self._validate_date(date)
            filename = name + ".log." + date

        path = self._log_dir / filename

        if require_exists:
            if not path.is_file():
                raise FileNotFoundError(
                    "log file does not exist: " + str(path)
                )

        return path

    @staticmethod
    def _validate_log_name(log_name: str) -> str:
        if not isinstance(log_name, str):
            raise ValueError("log_name must be a non-empty string")

        if log_name == "":
            raise ValueError("log_name must be a non-empty string")

        if Path(log_name).name != log_name:
            raise ValueError("log_name must not contain a path")

        if log_name == "." or log_name == "..":
            raise ValueError("log_name must not contain a path")

        if ".log" in log_name:
            raise ValueError("log_name must not contain '.log'")

        return log_name

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
    def _is_date(value: str) -> bool:
        try:
            LogCtrl._validate_date(value)
        except (TypeError, ValueError):
            return False

        return True

    @staticmethod
    def _parse_log_filename(filename: str):
        if filename.endswith(".log"):
            log_name = filename[:-4]

            if log_name != "":
                return log_name, None

            return None

        marker = ".log."

        if marker not in filename:
            return None

        log_name, date_value = filename.rsplit(marker, 1)

        if log_name == "":
            return None

        if not LogCtrl._is_date(date_value):
            return None

        return log_name, date_value
