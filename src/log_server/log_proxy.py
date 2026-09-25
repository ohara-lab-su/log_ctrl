#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DeviceClass 名を固定して LogServer を操作する LogProxy。"""

from __future__ import annotations

from typing import Any, Optional, Sequence, Tuple

from grpc_frame.grpc_client import SyncGrpcClient


class LogProxy:
    """DeviceClass ごとのログアクセスを提供する薄い Proxy。"""

    def __init__(
        self,
        device_class: str,
        server_ip: str,
        server_port: int,
        timeout_sec: Optional[float] = None,
        logger: Optional[Any] = None,
        log_level: Optional[str] = None,
        grpc_options: Optional[Sequence[Tuple[str, Any]]] = None,
    ) -> None:
        if not isinstance(device_class, str) or not device_class:
            raise ValueError("device_class must be a non-empty string")

        self._device_class = device_class
        self._client = SyncGrpcClient(
            server_ip=server_ip,
            server_port=server_port,
            timeout_sec=timeout_sec,
            logger=logger,
            log_level=log_level,
            grpc_options=grpc_options,
        )

    def read(self, date: Optional[str] = None) -> str:
        """現在ログ、または指定日のローテーション済みログを取得する。"""
        return self._client.read(self._device_class, date=date)

    def tail(
        self,
        lines: int = 100,
        date: Optional[str] = None,
    ) -> str:
        """現在ログ、または指定日のログ末尾を取得する。"""
        return self._client.tail(self._device_class, lines=lines, date=date)

    def dates(self) -> list[str]:
        """取得可能なローテーション済みログの日付一覧を返す。"""
        return self._client.dates(self._device_class)

    def exists(self, date: Optional[str] = None) -> bool:
        """現在ログ、または指定日のログが存在するか返す。"""
        return self._client.exists(self._device_class, date=date)

    def close(self) -> None:
        """gRPC channel を閉じる。"""
        self._client.close()

    def __enter__(self) -> "LogProxy":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
