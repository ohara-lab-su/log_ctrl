#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Iterator, Optional, Union

import grpc
from grpc import channel_ready_future

from grpc_frame.grpc_server import create_grpc_server

from log_ctrl.log_ctrl import LogCtrl


class _LogStream:
    """LogCtrl のログファイル本体を StreamCall 用チャンクとして返す。"""

    def __init__(
        self,
        ctrl: LogCtrl,
        chunk_size: int = 256 * 1024,
    ) -> None:
        if isinstance(chunk_size, bool):
            raise ValueError("chunk_size must be a positive integer")

        if not isinstance(chunk_size, int):
            raise ValueError("chunk_size must be a positive integer")

        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")

        self._ctrl = ctrl
        self._chunk_size = chunk_size

    def read(
        self,
        log_name: str,
        date: Optional[str] = None,
    ) -> Iterator[bytes]:
        path = self._ctrl._resolve_log_path(log_name, date)

        with path.open("rb") as file_obj:
            while True:
                chunk = file_obj.read(self._chunk_size)

                if not chunk:
                    break

                yield chunk

    def read_raw(
        self,
        relative_path: str,
    ) -> Iterator[bytes]:
        path = self._ctrl._resolve_raw_path(relative_path)

        with path.open("rb") as file_obj:
            while True:
                chunk = file_obj.read(self._chunk_size)

                if not chunk:
                    break

                yield chunk


def log_grpc_server(
    *,
    grpc_host: str,
    grpc_port: int,
    log_dir: Union[str, Path],
    encoding: str = "utf-8",
    chunk_size: int = 256 * 1024,
    logger: Optional[Any] = None,
    log_level: Optional[str] = None,
) -> None:
    """LogCtrl を grpc_frame 上で公開するログサーバーを起動する。"""
    if logger is None:
        import logging

        if log_level is None:
            log_level = "INFO"

        logging.basicConfig(level=log_level.upper())
        logger = logging.getLogger(__name__)

    ctrl = LogCtrl(
        log_dir=log_dir,
        encoding=encoding,
    )

    stream_obj = _LogStream(
        ctrl=ctrl,
        chunk_size=chunk_size,
    )

    server = create_grpc_server(
        ctrl_obj=ctrl,
        stream_obj=stream_obj,
        logger=logger,
        log_level=log_level,
        max_workers=10,
    )

    bind_addr = str(grpc_host) + ":" + str(grpc_port)

    ret = server.add_insecure_port(bind_addr)

    if ret == 0:
        raise RuntimeError("bind failed: " + bind_addr)

    logger.info("gRPC bind OK: " + bind_addr)

    server.start()

    ch = grpc.insecure_channel(bind_addr)
    channel_ready_future(ch).result(timeout=2.0)
    ch.close()

    logger.info("gRPC self-check OK")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

    finally:
        server.stop(grace=None)
        logger.info("gRPC server stopped")


log_server = log_grpc_server
