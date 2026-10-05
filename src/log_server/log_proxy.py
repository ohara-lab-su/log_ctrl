#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""logger_name を固定して LogServer を操作する LogProxy。"""

from typing import Any, List, Optional, Sequence, Tuple

from grpc_frame.grpc_client import GrpcClient


class LogProxy:
    """一つの logical logger へアクセスする Proxy。"""

    def __init__(
        self,
        logger_name: str,
        server_ip: str,
        server_port: int,
        timeout_sec: Optional[float] = None,
        logger: Optional[Any] = None,
        log_level: Optional[str] = None,
        grpc_options: Optional[Sequence[Tuple[str, Any]]] = None,
    ) -> None:
        if not isinstance(logger_name, str) or not logger_name:
            raise ValueError("logger_name must be a non-empty string")

        self._logger_name = logger_name

        self._client = GrpcClient(
            server_ip=server_ip,
            server_port=server_port,
            timeout_sec=timeout_sec,
            logger=logger,
            log_level=log_level,
            grpc_options=grpc_options,
        )

    def read(self, date: Optional[str] = None) -> str:
        """現在または指定日のログ全文を取得する。"""
        chunks = self._client.stream_call(
            "read",
            self._logger_name,
            date=date,
        )
        return "".join(chunks)

    def tail(
        self,
        lines: int = 100,
        date: Optional[str] = None,
    ) -> str:
        """現在または指定日のログ末尾を取得する。"""
        return self._client.tail(
            self._logger_name,
            lines=lines,
            date=date,
        )

    def dates(self) -> List[str]:
        """取得可能なローテーション済みログの日付を返す。"""
        return self._client.dates(self._logger_name)

    def exists(self, date: Optional[str] = None) -> bool:
        """現在または指定日のログが存在するか返す。"""
        return self._client.exists(self._logger_name, date=date)

    def close(self) -> None:
        """gRPC channel を閉じる。"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
