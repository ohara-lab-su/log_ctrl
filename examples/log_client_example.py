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
        log_names = client.log_names()
        print("log names:")
        print(log_names)

        if len(log_names) == 0:
            print("no log files")
            return

        log_name = log_names[0]
        print("selected log name:")
        print(log_name)
        print("-----------------------------")

        dates = client.dates(log_name)
        print("dates:")
        print(dates)
        print("-----------------------------")

        print("raw files:")
        print(client.raw_files())
        print("-----------------------------")

        print("current log:")
        data = client.read(log_name)
        print("bytes:", len(data))
        print("-----------------------------")

        if len(dates) > 0:
            date = dates[-1]
            print("historical log:")
            print(date)

            old_data = client.read(
                log_name,
                date=date,
            )
            print("bytes:", len(old_data))

            raw_filename = log_name + ".log." + date

            print("raw read:")
            print(raw_filename)

            raw_data = client.read_raw(raw_filename)
            print("bytes:", len(raw_data))
        print("-----------------------------")

    finally:
        client.close()


if __name__ == "__main__":
    main()
