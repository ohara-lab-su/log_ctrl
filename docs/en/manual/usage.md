# Usage

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/log_ctrl/en/manual/usage.html)  [![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/log_ctrl/ja/manual/usage.html)


## Server

The public server startup function is:
`log_ctrl.server_grpc.log_grpc_server()`.

``` python
from log_ctrl.server_grpc import log_grpc_server

log_grpc_server(
    grpc_host="0.0.0.0",
    grpc_port=50060,
    log_dir=r"C:\opt\ese774\log",
    encoding="utf-8",
    chunk_size=256 * 1024,
)
```

### `grpc_host`

The interface to which the gRPC server binds.

### `grpc_port`

The gRPC server port number.

### `log_dir`

The log directory to access.

The directory is checked when `LogCtrl` is constructed. If it does not exist,
`NotADirectoryError` is raised.

### `encoding`

The text encoding used by `tail()` to decode file contents into `str`.

`read()` and `read_raw()` transfer files as binary data, so their return type is
`bytes`.

### `chunk_size`

The number of bytes read per chunk during server streaming for `read()` and `read_raw()`.
This controls the size of each streamed chunk.

Default:

``` text
256 * 1024 bytes
```

This splits large log files into chunks instead of sending them as a single gRPC message.

### `logger` / `log_level`

If `logger` is supplied, that logger is used. When `logger=None`,
standard `logging` is used.

## DeviceProxy

Synchronous client:

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

`DeviceProxy("log", ...)` creates the registered `SyncLogGrpcClient` or
`AsyncLogGrpcClient`.

## `log_names()`

``` python
log_names = client.log_names()
```

Return type:

``` text
List[str]
```

Returns distinct `log_name` values extracted from `*.log` and `*.log.YYYY-MM-DD`,
sorted by name.

## `dates(log_name)`

``` python
dates = client.dates(
    "cobotta4_server"
)
```

Return type:

``` text
List[str]
```

Returns dates for existing rotated logs, newest first.

## `exists(log_name, date=None)`

Current log:

``` python
exists = client.exists(
    "cobotta4_server"
)
```

Specified date:

``` python
exists = client.exists(
    "cobotta4_server",
    date="2026-04-06",
)
```

Returns `bool`.

## `tail(log_name, lines=100, date=None)`

Current log:

``` python
text = client.tail(
    "cobotta4_server",
    lines=100,
)
```

Specified date:

``` python
text = client.tail(
    "cobotta4_server",
    lines=100,
    date="2026-04-06",
)
```

Returns `str`.

`lines` must be a positive integer.

## `raw_files()`

``` python
files = client.raw_files()
```

Return type:

``` text
List[str]
```

Recursively scans `log_dir` and returns relative paths for all files.

This troubleshooting API shows the actual directory contents rather than parsing log names.

## `read(log_name, date=None)`

Current log:

``` python
data = client.read(
    "cobotta4_server"
)
```

Specified date:

``` python
data = client.read(
    "cobotta4_server",
    date="2026-04-06",
)
```

Returns `bytes`.

Internally, the `grpc_frame` `StreamCall` mechanism
transfers the file in chunks, which the device-specific client reassembles.

To decode the data as text:

``` python
text = data.decode("utf-8")
```

## `read_raw(relative_path)`

``` python
data = client.read_raw(
    "cobotta4_server.log.2026-04-06"
)
```

Supply a relative path returned by `raw_files()` to retrieve the file contents.

Files in subdirectories can also be specified by relative path, but paths escaping `log_dir`
are rejected.

Returns `bytes`.

## Closing the client

``` python
client.close()
```

Closes the `grpc_frame` channel.

## Asynchronous client

``` python
client = DeviceProxy(
    "log",
    server_ip="127.0.0.1",
    server_port=50060,
    set_timeout_sec=10.0,
    async_mode=True,
)
```

With `AsyncLogGrpcClient`, both `read()` and `read_raw()` must also be
awaited.

``` python
data = await client.read(
    "cobotta4_server"
)
```

Methods bound automatically as ordinary RPCs follow the `grpc_frame`
asynchronous client API.
