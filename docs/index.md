# log_ctrl

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/log_ctrl/)
[![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/log_ctrl/ja/)

[GitHub repository](https://github.com/ohara-lab-su/log_ctrl/) · [Project documentation](https://ohara-lab-su.github.io/)

`log_ctrl` retrieves logs written by DeviceServer through `x_logger` using a separate gRPC LogServer, independently of
DeviceServer.

```{toctree}
:maxdepth: 2
:caption: Guides

manual/quickstart
manual/architecture
manual/usage
manual/rotation
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/index
```

## Design policy

DeviceServer remains responsible for transparent device operations, not log distribution.
LogCtrl accesses the specified log directory in read-only mode.

```text
DeviceServer A ─ x_logger ─┐
DeviceServer B ─ x_logger ─┼─ log directory ← LogServer ← gRPC ← LogProxy
DeviceServer C ─ x_logger ─┘
```
