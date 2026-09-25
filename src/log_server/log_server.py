#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""x_logger の保存ログを公開する gRPC ログサーバー。

DeviceServer とは独立したプロセスとして起動し、同一ホスト上の
x_logger が保存したログファイルを read-only で公開する。

x_logger の rotating mode は TimedRotatingFileHandler(when="midnight") を
使用しているため、標準では次の命名を前提とする。

    <device_class>.log
    <device_class>.log.YYYY-MM-DD

ログ保存ディレクトリは LogServer(log_dir=...) で明示指定できる。
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional


class LogServer:
    """x_logger が保存したデバイスログを読み出すコントローラ。"""

    def __init__(
        self,
        log_dir: str | Path,
        *,
        log_suffix: str = ".log",
        encoding: str = "utf-8",
    ) -> None:
        """初期化する。

        Args:
            log_dir: x_logger の log_name で使用している保存ディレクトリ。
            log_suffix: DeviceClass 名の後ろに付くログファイル接尾辞。
                既定値は ``.log``。
            encoding: ログファイルの文字コード。x_logger の既定に合わせて
                ``utf-8`` を使用する。
        """
        self._log_dir = Path(log_dir).expanduser().resolve()
        self._log_suffix = str(log_suffix)
        self._encoding = str(encoding)

        if not self._log_dir.is_dir():
            raise NotADirectoryError(f"log directory does not exist: {self._log_dir}")

    def read(
        self,
        device_class: str,
        date: Optional[str] = None,
    ) -> str:
        """指定デバイスのログを取得する。

        Args:
            device_class: DeviceClass 名。
            date: ``YYYY-MM-DD``。None の場合は現在のログファイルを読む。

        Returns:
            ログ全文。
        """
        path = self._resolve_log_path(device_class=device_class, date_value=date)
        return path.read_text(encoding=self._encoding)

    def tail(
        self,
        device_class: str,
        lines: int = 100,
        date: Optional[str] = None,
    ) -> str:
        """指定ログの末尾を取得する。

        Args:
            device_class: DeviceClass 名。
            lines: 取得する行数。
            date: ``YYYY-MM-DD``。None の場合は現在のログファイルを読む。

        Returns:
            指定行数分のログ文字列。
        """
        if isinstance(lines, bool) or not isinstance(lines, int) or lines <= 0:
            raise ValueError("lines must be a positive integer")

        path = self._resolve_log_path(device_class=device_class, date_value=date)
        return self._tail_file(path=path, lines=lines)

    def dates(self, device_class: str) -> list[str]:
        """取得可能なローテーション済みログの日付一覧を返す。

        Args:
            device_class: DeviceClass 名。

        Returns:
            ``YYYY-MM-DD`` の降順リスト。
        """
        base_name = self._base_name(device_class)
        prefix = f"{base_name}."
        found: list[str] = []

        for path in self._log_dir.glob(f"{base_name}.*"):
            suffix = path.name[len(prefix) :]
            if self._is_date_string(suffix):
                found.append(suffix)

        return sorted(found, reverse=True)

    def exists(
        self,
        device_class: str,
        date: Optional[str] = None,
    ) -> bool:
        """指定ログが存在するか返す。"""
        try:
            path = self._resolve_log_path(
                device_class=device_class,
                date_value=date,
                require_exists=False,
            )
        except (TypeError, ValueError):
            return False
        return path.is_file()

    def _base_name(self, device_class: str) -> str:
        """DeviceClass から現在ログのファイル名を作る。"""
        if not isinstance(device_class, str) or not device_class:
            raise ValueError("device_class must be a non-empty string")

        # DeviceClass はファイル名としてのみ扱う。パス指定は許可しない。
        if Path(device_class).name != device_class or device_class in {".", ".."}:
            raise ValueError("device_class must not contain a path")

        return f"{device_class}{self._log_suffix}"

    def _resolve_log_path(
        self,
        *,
        device_class: str,
        date_value: Optional[str],
        require_exists: bool = True,
    ) -> Path:
        """DeviceClass と日付から x_logger のログパスを解決する。"""
        base_name = self._base_name(device_class)

        if date_value is None:
            path = self._log_dir / base_name
        else:
            self._validate_date(date_value)
            path = self._log_dir / f"{base_name}.{date_value}"

        if require_exists and not path.is_file():
            raise FileNotFoundError(f"log file does not exist: {path.name}")

        return path

    @staticmethod
    def _validate_date(value: str) -> None:
        """YYYY-MM-DD 形式の日付を検証する。"""
        if not isinstance(value, str):
            raise TypeError("date must be a string in YYYY-MM-DD format")
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("date must be in YYYY-MM-DD format") from exc
        if parsed.strftime("%Y-%m-%d") != value:
            raise ValueError("date must be in YYYY-MM-DD format")

    @staticmethod
    def _is_date_string(value: str) -> bool:
        try:
            LogServer._validate_date(value)
        except (TypeError, ValueError):
            return False
        return True

    def _tail_file(self, *, path: Path, lines: int) -> str:
        """ファイル全体を読み込まず末尾 N 行を取得する。"""
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


def create_log_grpc_server(
    *,
    log_dir: str | Path,
    log_suffix: str = ".log",
    encoding: str = "utf-8",
    max_workers: int = 10,
    logger: Optional[Any] = None,
    log_level: Optional[str] = None,
    grpc_options=None,
):
    """LogServer を載せた grpc_frame サーバーを生成する。

    既存の ``create_grpc_server`` をそのまま利用し、DeviceServer の実装には
    変更を加えない。
    """
    from grpc_frame.grpc_server import create_grpc_server

    controller = LogServer(
        log_dir=log_dir,
        log_suffix=log_suffix,
        encoding=encoding,
    )
    return create_grpc_server(
        ctrl_obj=controller,
        max_workers=max_workers,
        logger=logger,
        log_level=log_level,
        grpc_options=grpc_options,
    )
