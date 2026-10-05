#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from log_ctrl.server_grpc import log_grpc_server
from x_logger import XLogger

if __name__ == "__main__":
    # GRPC_HOST = "0.0.0.0"
    GRPC_HOST = "10.170.10.41"
    GRPC_PORT = 50060
    LOG_DIR = r"C:\opt\ese774\log"

    logger = XLogger(
        logger_name="log_server",
    )

    log_grpc_server(
        grpc_host=GRPC_HOST,
        grpc_port=GRPC_PORT,
        log_dir=LOG_DIR,
        logger=logger,
    )
