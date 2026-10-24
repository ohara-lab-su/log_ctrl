# Quick Start

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/log_ctrl/en/manual/quickstart.html)  [![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/log_ctrl/ja/manual/quickstart.html)


## 1. Check the log directory

For example, assume the log directory contains:

``` text
C:\opt\ese774\log\
├── cobotta3_server2.log
├── cobotta3_server2.log.2026-02-19
├── cobotta4_server.log
├── cobotta4_server.log.2026-04-06
├── cobotta4_server2.log
└── cobotta4_server2.log.2026-06-16
```

The current log uses:

``` text
<log_name>.log
```

A rotated log uses:

``` text
<log_name>.log.YYYY-MM-DD
```

These are the supported filename forms.

## 2. Start LogServer

``` python
from log_ctrl.server_grpc import log_grpc_server

GRPC_HOST = "0.0.0.0"
GRPC_PORT = 50060
LOG_DIR = r"C:\opt\ese774\log"

log_grpc_server(
    grpc_host=GRPC_HOST,
    grpc_port=GRPC_PORT,
    log_dir=LOG_DIR,
)
```

`LOG_DIR`
`LOG_DIR` must point to an existing log directory. If it does not exist, constructing `LogCtrl`
raises `NotADirectoryError`.

## 3. Create a client

``` python
from log_ctrl.server_grpc import DeviceProxy

client = DeviceProxy(
    "log",
    server_ip="127.0.0.1",
    server_port=50060,
    set_timeout_sec=10.0,
    async_mode=False,
)
```

`"log"` is the DeviceProxy name registered by `log_ctrl.server_grpc`
through `register_device_proxy()`.

## 4. List available `log_name` values

Instead of hardcoding log names, first inspect which logs actually exist on the server.

``` python
log_names = client.log_names()
print(log_names)
```

Example:

``` text
[
    "cobotta3_server2",
    "cobotta4_server",
    "cobotta4_server2",
]
```

## 5. List available dates

``` python
log_name = log_names[0]

dates = client.dates(log_name)
print(dates)
```

`dates()` returns only dates for existing `<log_name>.log.YYYY-MM-DD`
files. The current `<log_name>.log` is not included.

## 6. Read the current log

`log_names()` can include a `log_name` for which only rotated files remain.
Before reading a current log, use `exists()`
to check whether the file is present.

``` python
if client.exists(log_name):
    data = client.read(log_name)
    print("bytes:", len(data))
```

`read()` returns `bytes`.

To handle the contents as text:

``` python
text = data.decode("utf-8")
print(text)
```

## 7. Read a rotated log

``` python
dates = client.dates(log_name)

if len(dates) > 0:
    date = dates[0]

    data = client.read(
        log_name,
        date=date,
    )

    print("date:", date)
    print("bytes:", len(data))
```

`dates()` returns dates in descending order, so `dates[0]`
is the newest available date.

## 8. Inspect actual files for troubleshooting

``` python
files = client.raw_files()
print(files)
```

`raw_files()` is not limited to files recognized as logs; it returns relative paths for all files
under `log_dir`.

You can pass one of these relative paths directly to `read_raw()`.

``` python
data = client.read_raw(
    "cobotta4_server.log.2026-04-06"
)
```

## 9. Close the client

``` python
client.close()
```

Normally, use `try` / `finally` to ensure that the client is closed.

``` python
try:
    print(client.log_names())
finally:
    client.close()
```
