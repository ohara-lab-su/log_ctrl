# Rotation

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/log_ctrl/en/manual/rotation.html)  [![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/log_ctrl/ja/manual/rotation.html)


`log_ctrl` recognizes the following two log filename formats:

``` text
<log_name>.log
<log_name>.log.YYYY-MM-DD
```

Examples:

``` text
cobotta4_server.log
cobotta4_server.log.2026-03-31
cobotta4_server.log.2026-04-06
```

## Current log

A file without a date suffix,

``` text
<log_name>.log
```

is the current log.

The current log has no special date such as `current`
and no virtual filename.

``` python
data = client.read("cobotta4_server")
```

reads:

``` text
cobotta4_server.log
```

This is the current log file.

## Rotated logs

``` python
data = client.read(
    "cobotta4_server",
    date="2026-04-06",
)
```

reads:

``` text
cobotta4_server.log.2026-04-06
```

This is the dated log file.

Dates are strictly validated in `YYYY-MM-DD` format.

## Listing dates

``` python
dates = client.dates(
    "cobotta4_server"
)
```

`dates()` examines existing files matching:

``` text
<log_name>.log.YYYY-MM-DD
```

and returns only files with valid date suffixes.

The results are sorted newest first.

``` text
[
    "2026-04-06",
    "2026-03-31",
    "2026-03-30",
]
```

Dates need not be consecutive; missing dates are not filled in.

The current `<log_name>.log` is not included in `dates()`.

## `log_names()`

`log_names()` extracts `log_name` values from both current
and rotated logs.

Therefore, if only:

``` text
old_device.log.2026-02-19
```

exists, and:

``` text
old_device.log
```

does not exist,

``` python
client.log_names()
```

still includes `"old_device"`.

Check separately whether the current log exists using:

``` python
client.exists("old_device")
```

This call tests the current file.

## Responsibility for rotation

`log_ctrl` itself does not perform:

-   Writing logs
-   Rotating logs
-   Managing the number of retained generations
-   Deleting old logs

These operations are outside its scope.

They are the responsibility of the log-writing process. `log_ctrl`
only accesses files that actually exist in the directory.

## Files outside the naming convention

`log_names()` and `dates()`
parse only files matching the log naming convention above.

For troubleshooting, however:

``` python
client.raw_files()
```

returns every file under `log_dir`, without filtering by filename.

Consequently, even a file outside the naming convention can be read with:

``` python
client.read_raw(relative_path)
```

This retrieves its contents.

## Path restrictions

For ordinary `read()`, `tail()`, `exists()`, and `dates()` calls, `log_name`
cannot contain a path. The `log_name` itself also cannot include
`.log`.

`read_raw()` accepts a relative path, but rejects paths that resolve outside `log_dir`.
Absolute paths are also prohibited.
