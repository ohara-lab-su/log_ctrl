# CHANGELOG

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/log_ctrl/blob/main/CHANGELOG.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/log_ctrl/blob/main/CHANGELOG.ja.md)

## v0.0.1

Preparation for publication on PyPI.

### Changes

- Prepared the package for publication on PyPI.
- Added the English README (`README.en.md`).
- Added the changelog.
- Added a Japanese changelog (`CHANGELOG.md`) and an English changelog (`CHANGELOG.en.md`).

There are no functional changes in this version.

## v0.0.0

Initial version.

### Implemented

- Read-only access to a log directory through `LogCtrl`.
- Discovery of `log_name` values from current and rotated log files.
- Retrieval of rotation dates for a specified `log_name`.
- Existence checks for current and date-specific log files.
- `tail()` for retrieving the end of a log.
- `raw_files()` for listing files under the log directory as relative
  paths.
- `read()` for retrieving log files as `bytes`.
- `read_raw()` for retrieving a file specified by a relative path as
  `bytes`.
- Path validation to prevent access outside the configured log
  directory.
- An independent log gRPC server based on `grpc_frame`.
- Chunked log-file transfer using `StreamCall`.
- Synchronous gRPC client `SyncLogGrpcClient`.
- Asynchronous gRPC client `AsyncLogGrpcClient`.
