#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
from typing import Any, Optional, Sequence, Tuple

from grpc_frame import AsyncGrpcClient


class AsyncLogGrpcClient(AsyncGrpcClient):
    """ログサーバー用 AsyncGrpcClient。"""

    def __init__(
        self,
        server_ip: str,
        server_port: int,
        timeout_sec: Optional[float] = None,
        logger: Optional[Any] = None,
        log_level: Optional[str] = None,
        grpc_options: Optional[Sequence[Tuple[str, Any]]] = None,
        set_timeout_sec: Optional[float] = None,
    ) -> None:
        if timeout_sec is not None and set_timeout_sec is not None:
            raise ValueError(
                "timeout_sec and set_timeout_sec cannot be specified together"
            )

        effective_timeout_sec = set_timeout_sec

        if timeout_sec is not None:
            effective_timeout_sec = timeout_sec

        super().__init__(
            server_ip=server_ip,
            server_port=server_port,
            timeout_sec=effective_timeout_sec,
            logger=logger,
            log_level=log_level,
            grpc_options=grpc_options,
        )

    def _read_sync(
        self,
        log_name: str,
        date: Optional[str] = None,
    ) -> bytes:
        data = bytearray()

        for chunk in self.stream_call(
            "read",
            log_name,
            date=date,
        ):
            data.extend(chunk)

        return bytes(data)

    def _read_raw_sync(
        self,
        relative_path: str,
    ) -> bytes:
        data = bytearray()

        for chunk in self.stream_call(
            "read_raw",
            relative_path,
        ):
            data.extend(chunk)

        return bytes(data)

    async def read(
        self,
        log_name: str,
        date: Optional[str] = None,
    ) -> bytes:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._read_sync,
            log_name,
            date,
        )

    async def read_raw(
        self,
        relative_path: str,
    ) -> bytes:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._read_raw_sync,
            relative_path,
        )
