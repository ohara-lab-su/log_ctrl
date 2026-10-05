#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Optional, Union
from pathlib import Path

from grpc_frame import DeviceProxy, register_device_proxy

from log_ctrl.server_grpc.async_log_grpc_client import AsyncLogGrpcClient
from log_ctrl.server_grpc.sync_log_grpc_client import SyncLogGrpcClient

DEVICE_PROXY_NAME = "log"
DEVICE_PROXY_ALIASES = [
    "Log",
    "LogCtrl",
    "log_grpc",
]

register_device_proxy(
    DEVICE_PROXY_NAME,
    async_client_cls=AsyncLogGrpcClient,
    sync_client_cls=SyncLogGrpcClient,
    default_async_mode=False,
    aliases=DEVICE_PROXY_ALIASES,
)


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
    from log_ctrl.server_grpc.log_grpc_server import log_grpc_server as _server

    _server(
        grpc_host=grpc_host,
        grpc_port=grpc_port,
        log_dir=log_dir,
        encoding=encoding,
        chunk_size=chunk_size,
        logger=logger,
        log_level=log_level,
    )


def log_server(
        *,
        grpc_host: str,
        grpc_port: int,
        log_dir: Union[str, Path],
        encoding: str = "utf-8",
        chunk_size: int = 256 * 1024,
        logger: Optional[Any] = None,
        log_level: Optional[str] = None,
) -> None:
    log_grpc_server(
        grpc_host=grpc_host,
        grpc_port=grpc_port,
        log_dir=log_dir,
        encoding=encoding,
        chunk_size=chunk_size,
        logger=logger,
        log_level=log_level,
    )


__all__ = [
    "DEVICE_PROXY_NAME",
    "DEVICE_PROXY_ALIASES",
    "DeviceProxy",
    "AsyncLogGrpcClient",
    "SyncLogGrpcClient",
    "log_grpc_server",
    "log_server",
]
