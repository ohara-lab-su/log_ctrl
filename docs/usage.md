# Usage

## LogServer

```python
server = create_log_grpc_server(
    log_dir="/var/log/device_servers",
    log_suffix=".log",
    encoding="utf-8",
    chunk_size=256 * 1024,
    max_workers=10,
)
```

### `log_dir`

ログを保存しているディレクトリです。固定値ではなく起動時に指定します。

### `log_suffix`

現在の標準は `.log` です。DeviceClass が `Cobotta` なら `Cobotta.log` を基準名とします。

### `chunk_size`

`LogStream.read()` が一度に読む文字数です。ログ全文は server-streaming で送信されます。

## LogProxy

```python
log = LogProxy(
    "Cobotta",
    server_ip="127.0.0.1",
    server_port=50060,
)
```

### 現在ログ

```python
text = log.read()
```

### 指定日のログ

```python
text = log.read(date="2026-09-24")
```

### 末尾

```python
text = log.tail(lines=100)
```

### 保存日一覧

```python
dates = log.dates()
```

### 存在確認

```python
if log.exists(date="2026-09-24"):
    ...
```

### 終了

```python
log.close()
```

context manager も使用できます。

```python
with LogProxy(...) as log:
    ...
```
