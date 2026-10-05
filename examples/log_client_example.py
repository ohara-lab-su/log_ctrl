#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LogProxy 使用例。"""

from log_proxy import LogProxy


with LogProxy(
    "Cobotta",
    server_ip="127.0.0.1",
    server_port=50060,
) as log:
    print(log.tail(lines=100))
    print(log.dates())
    print(log.read(date="2026-09-24"))
