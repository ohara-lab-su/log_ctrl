# log_ctrl

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/log_ctrl/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/log_ctrl/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Flog_ctrl-181717?logo=github)](https://github.com/ohara-lab-su/log_ctrl/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/log_ctrl/en/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.en.html)

`log_ctrl` is a package for accessing log files stored in a specified
log directory over a network using `grpc_frame`.

It does not add log retrieval RPCs to the DeviceServer or application
that writes the logs. `log_ctrl` runs as an independent, read-only gRPC
server that accesses existing log files.

``` text
application / DeviceServer
        │
        │ write
        ▼
C:\opt\ese774\log
├── cobotta4_server.log
├── cobotta4_server.log.2026-04-06
├── cobotta4_server2.log
└── cobotta4_server2.log.2026-06-16
        ▲
        │ read only
        │
     LogCtrl
        │
        ▼
 log gRPC server
        │
        ▼
DeviceProxy("log", ...)
```

## Log names

In `log_ctrl`, the part before `.log` is called the `log_name`.

``` text
cobotta4_server.log
^^^^^^^^^^^^^^^
   log_name
```

Rotated log files use the following format:

``` text
<log_name>.log.YYYY-MM-DD
```

The `log_name` does not need to match the DeviceServer name or device
class name. `log_ctrl` uses the `log_name` exactly as it appears in the
filename.

## Main features

- `log_names()`: Get the list of `log_name` values from existing log
  files.
- `dates(log_name)`: Get the list of rotation dates for the specified
  `log_name`.
- `exists(log_name, date=None)`: Check whether the current log or a
  log for a specified date exists.
- `tail(log_name, lines=100, date=None)`: Get the end of a log as a
  string.
- `raw_files()`: List all files under the log directory as relative
  paths.
- `read(log_name, date=None)`: Read a log file as `bytes`.
- `read_raw(relative_path)`: Read an arbitrary file confirmed by
  `raw_files()` as `bytes`.

Large log files are transferred in chunks using `grpc_frame`
`StreamCall`. Client-side code does not need to handle the stream
directly; `read()` and `read_raw()` join the received chunks and return
them as `bytes`.

## Installation

Install in an environment where `grpc_frame` is available.

``` bash
python -m pip install .
```

For development, use an editable install:

``` bash
python -m pip install -e .
```

## Starting LogServer

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

If `logger` is omitted, the standard `logging` module is used. To use an
existing logger, pass it with `logger=`.

## Client

Use `DeviceProxy` as the transparent `grpc_frame` client.

``` python
from log_ctrl.server_grpc import DeviceProxy

client = DeviceProxy(
    "log",
    server_ip="127.0.0.1",
    server_port=50060,
    set_timeout_sec=10.0,
    async_mode=False,
)

try:
    log_names = client.log_names()
    print(log_names)

    if len(log_names) > 0:
        log_name = log_names[0]

        print(client.dates(log_name))

        if client.exists(log_name):
            data = client.read(log_name)
            print(len(data))

finally:
    client.close()
```

The names returned by `log_names()` are not limited to names for which a
current `<log_name>.log` file exists. A name is also included when only
rotated log files remain. Check `exists(log_name)` as needed before
reading the current log.

## API

``` python
client.log_names()
client.dates(log_name)

client.exists(log_name)
client.exists(log_name, date="2026-04-06")

client.tail(log_name, lines=100)
client.tail(log_name, lines=100, date="2026-04-06")

client.raw_files()

client.read(log_name)
client.read(log_name, date="2026-04-06")

client.read_raw("cobotta4_server.log.2026-04-06")
```

`read()` and `read_raw()` return `bytes`. To handle a log as text,
decode it on the client using the appropriate character encoding.

``` python
text = client.read(log_name).decode("utf-8")
```

`tail()` is decoded on the server using the configured `encoding` and
returns `str`.

## Documentation

Sphinx documentation is available under `docs/`.

- `docs/index.md`
- `docs/quickstart.md`
- `docs/usage.md`
- `docs/rotation.md`
- `docs/architecture.md`

## License

See `LICENSE`.
