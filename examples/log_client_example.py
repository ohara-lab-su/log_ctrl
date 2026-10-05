#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from log_ctrl.server_grpc import DeviceProxy


def main() -> None:
    client = DeviceProxy(
        "log",
        # server_ip="127.0.0.1",
        server_ip="10.170.10.41",
        server_port=50060,
        set_timeout_sec=10.0,
        async_mode=False,
    )

    try:
        print(client.log_names())
        print(client.dates("aandd"))
        raw_files = client.raw_files()
        print(raw_files)

        data = client.read("aandd")
        print(len(data))

        old_data = client.read(
            "aandd",
            date="2026-10-01",
        )
        print(len(old_data))

        raw_data = client.read_raw("aandd.log.2026-10-01")
        print(len(raw_data))

    finally:
        client.close()


if __name__ == "__main__":
    main()
