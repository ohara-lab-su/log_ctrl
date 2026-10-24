# Architecture

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/log_ctrl/en/manual/architecture.html)  [![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/log_ctrl/ja/manual/architecture.html)


## Overall architecture

`log_ctrl` operates independently of the process that writes the logs.

``` text
┌───────────────────────────┐
│ application / DeviceServer│
│ logger                    │
└─────────────┬─────────────┘
              │ write
              ▼
       log directory
              ▲
              │ read only
              │
┌─────────────┴─────────────┐
│ log_ctrl                  │
│                           │
│ LogCtrl                   │
│   ├─ log_names()          │
│   ├─ dates()              │
│   ├─ raw_files()          │
│   ├─ exists()             │
│   └─ tail()               │
│                           │
│ _LogStream                │
│   ├─ read()               │
│   └─ read_raw()           │
└─────────────┬─────────────┘
              │
              │ grpc_frame
              ▼
┌───────────────────────────┐
│ DeviceProxy("log")        │
│                           │
│ SyncLogGrpcClient         │
│ AsyncLogGrpcClient        │
└───────────────────────────┘
```

No `log_ctrl`-specific RPC needs to be added to the log-writing process.

## `LogCtrl`

`LogCtrl` is a controller class that accesses the log directory locally.

Its principal state consists of:

-   `log_dir`
-   `encoding`

These are its configuration attributes.

On initialization, `log_dir` is normalized using `Path.resolve()`,
and verified to be an existing directory.

### Methods exposed as ordinary RPCs

``` text
log_names()
dates(log_name)
raw_files()
exists(log_name, date=None)
tail(log_name, lines=100, date=None)
```

These methods are bound to the client through the `grpc_frame`
Describe/Call mechanism.

`LogCtrl` contains no gRPC-specific
logic; as a local class it handles file discovery, validation, and reading log tails.

## `log_names()`

For files directly under `log_dir`, it parses:

``` text
<log_name>.log
<log_name>.log.YYYY-MM-DD
```

and builds the set of `log_name` values.

Names are discovered from both current and archived logs, so a name may be returned even if its current `.log`
file does not exist.

## `dates()`

For the specified `log_name`, the method searches for existing files matching:

``` text
<log_name>.log.YYYY-MM-DD
```

Only files matching this pattern are considered.

Date suffixes are validated with `datetime.strptime(..., "%Y-%m-%d")`
and returned in descending date order.

## `raw_files()`

`Path.rglob("*")` recursively scans the directory tree under `log_dir`.

No filename convention is applied; all files are returned as paths relative to
`log_dir`.

This provides a separate troubleshooting path for inspecting the actual file layout.

## `_LogStream`

File contents are not returned as one ordinary RPC response. Instead, the `grpc_frame`
`StreamCall` mechanism is used.

The streaming interface provides:

``` text
read(log_name, date=None)
read_raw(relative_path)
```

These are the streaming methods.

`read()` uses the normal log-path resolution in `LogCtrl`, while `read_raw()`
uses raw relative-path resolution.

The file is read in binary chunks of `chunk_size` bytes,

``` text
bytes
bytes
bytes
...
```

which are yielded in sequence.

## Client side

When `log_ctrl.server_grpc` is imported,

``` python
register_device_proxy(
    "log",
    async_client_cls=AsyncLogGrpcClient,
    sync_client_cls=SyncLogGrpcClient,
    ...
)
```

registers the log client with `DeviceProxy`.

The caller only needs to create:

``` python
client = DeviceProxy(
    "log",
    server_ip="127.0.0.1",
    server_port=50060,
    async_mode=False,
)
```

to obtain the log-specific client.

### Ordinary RPCs

`log_names()`, `dates()`, `raw_files()`, `exists()`, and `tail()`
are bound transparently by `grpc_frame` from the `LogCtrl` Describe metadata.

### File contents

`read()` and `read_raw()` are implemented by the device-specific clients.

The synchronous client iterates over `stream_call()` and appends chunks to a `bytearray`,
ultimately returning `bytes`.

Applications therefore do not need to handle `StreamCall` or chunk boundaries.

## Path resolution

An ordinary log path is resolved from:

``` text
log_name
    ↓
<log_name>.log
```

or:

``` text
log_name + date
    ↓
<log_name>.log.YYYY-MM-DD
```

These mappings determine the file path.

A `log_name` containing directory components or `.log` is rejected.

A relative path supplied to `read_raw()` is joined with `log_dir` and passed through `resolve()`;
the resolved path must remain inside `log_dir`. This prevents `../`
and similar paths from accessing files outside the log directory.

## Lifecycle

The server entry point `log_grpc_server()` performs the following steps:

1.  Create `LogCtrl`.
2.  Create the stream handler.
3.  Create the `grpc_frame` gRPC server.
4.  Bind to the requested host and port.
5.  Start the server.
6.  Verify startup with a self-connection.
7.  Wait until shutdown.

This sequence is managed by the server entry point.

The client is created with `DeviceProxy`. After use, call:

``` python
client.close()
```

to close the channel.
