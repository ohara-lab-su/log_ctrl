# log_ctrl

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/log_ctrl/)
[![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/log_ctrl/ja/)

[GitHub repository](https://github.com/ohara-lab-su/log_ctrl/) · [Project documentation](https://ohara-lab-su.github.io/)

`log_ctrl` は、DeviceServer が `x_logger` で保存したログを、DeviceServer とは独立した gRPC LogServer から取得するためのパッケージです。

```{toctree}
:maxdepth: 2
:caption: マニュアル

manual/quickstart
manual/architecture
manual/usage
manual/rotation
```

```{toctree}
:maxdepth: 2
:caption: APIリファレンス

api/index
```

## 設計方針

DeviceServer は機器操作の透過性を維持し、ログ配信の責務を持ちません。
LogCtrl は指定されたログディレクトリを read-only で参照します。

```text
DeviceServer A ─ x_logger ─┐
DeviceServer B ─ x_logger ─┼─ log directory ← LogServer ← gRPC ← LogProxy
DeviceServer C ─ x_logger ─┘
```
