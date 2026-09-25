# Quick Start

## 1. ログファイル

LogServer は次の形式を前提にします。

```text
/var/log/device_servers/
├── Cobotta.log
├── Cobotta.log.2026-09-24
├── Stage.log
└── Stage.log.2026-09-24
```

現在ログは `<DeviceClass>.log`、日次ローテーション済みログは
`<DeviceClass>.log.YYYY-MM-DD` です。

## 2. LogServer を起動する

```python
from log_server import create_log_grpc_server

server = create_log_grpc_server(
    log_dir="/var/log/device_servers",
)
server.add_insecure_port("[::]:50060")
server.start()
server.wait_for_termination()
```

## 3. ログを取得する

```python
from log_server import LogProxy

with LogProxy(
    "Cobotta",
    server_ip="127.0.0.1",
    server_port=50060,
) as log:
    print(log.tail(lines=100))
    print(log.dates())
    print(log.read(date="2026-09-24"))
```

`LogProxy` に指定する名前はログファイル名の基準となる DeviceClass 名です。
