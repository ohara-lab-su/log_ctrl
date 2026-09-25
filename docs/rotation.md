# Rotation

`log_server` は `x_logger` の日次ローテーションを前提とします。

```text
Cobotta.log
Cobotta.log.2026-09-24
Cobotta.log.2026-09-23
```

現在ログは日付 suffix を持ちません。ローテーション済みログの日付は
`YYYY-MM-DD` として検証されます。

`dates()` は `<DeviceClass>.log.*` を列挙した上で、正しい日付形式のファイルだけを返します。
無関係な suffix は除外されます。

```python
log.dates()
# ["2026-09-24", "2026-09-23", ...]
```

ローテーション数の管理は `x_logger` 側の責務です。LogServer は `backup_count` を管理せず、
実際に存在するファイルを読み取ります。

## セキュリティ

DeviceClass にパスを含めることはできません。`../Cobotta` のような指定は拒否されます。
これにより `log_dir` 外の任意ファイルを指定する経路を作らない設計になっています。
