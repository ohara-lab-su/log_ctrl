#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LogServer 起動例。"""

from log_server import create_log_grpc_server

LOG_DIR = "/var/log/device_servers"
PORT = 50060

server = create_log_grpc_server(log_dir=LOG_DIR)
server.add_insecure_port(f"[::]:{PORT}")
server.start()
server.wait_for_termination()
