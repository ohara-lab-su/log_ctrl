# log_ctrl

`log_ctrl` は、DeviceServer が `x_logger` で保存したログを、DeviceServer とは独立した
gRPC LogServer から取得するためのパッケージです。

```{toctree}
:maxdepth: 2
:caption: Contents

quickstart
architecture
usage
rotation
api/modules
```

## 設計方針

DeviceServer は機器操作の透過性を維持し、ログ配信の責務を持ちません。
LogCtrl は指定されたログディレクトリを read-only で参照します。

```text
DeviceServer A ─ x_logger ─┐
DeviceServer B ─ x_logger ─┼─ log directory ← LogServer ← gRPC ← LogProxy
DeviceServer C ─ x_logger ─┘
```
