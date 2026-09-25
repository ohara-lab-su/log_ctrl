# log_server

`log_server` は、各 DeviceServer が `x_logger` でローカル保存しているログを、
DeviceServer とは独立した gRPC サーバーから参照するためのパッケージです。

DeviceServer 自体にはログ取得機能を追加しません。各 DeviceServer は従来どおり
`x_logger` のインスタンスを持ち、ログファイルへ書き込みます。`log_server` は
そのファイルを read-only で参照します。

```text
DeviceServer("Cobotta")              LogServer
  └─ x_logger                           ├─ LogController
      ├─ Cobotta.log                    └─ LogStream
      └─ Cobotta.log.YYYY-MM-DD              ↑
                                              │ gRPC
                                           LogProxy("Cobotta")
```

## 前提となるログ形式

`x_logger` の `TimedRotatingFileHandler(when="midnight")` に合わせ、次の名前を扱います。

```text
<device_class>.log
<device_class>.log.YYYY-MM-DD
```

ログディレクトリは固定ではなく、LogServer 起動時に `log_dir` で指定します。

## 主な機能

- DeviceClass 名によるログ指定
- 現在ログの取得
- `YYYY-MM-DD` を指定したローテーション済みログの取得
- 利用可能なローテーション日付の一覧取得
- ログ末尾の取得
- ログ存在確認
- 大きなログ本文の gRPC server-streaming
- DeviceServer とは独立した LogServer プロセス

## インストール

本パッケージは `grpc_frame` を利用します。`grpc_frame` を利用可能な環境で、
このプロジェクトをインストールしてください。

```bash
python -m pip install .
```

開発用:

```bash
python -m pip install -e .
```

## LogServer の起動

```python
from log_server import create_log_grpc_server

LOG_DIR = "/var/log/device_servers"
PORT = 50060

server = create_log_grpc_server(log_dir=LOG_DIR)
server.add_insecure_port(f"[::]:{PORT}")
server.start()
server.wait_for_termination()
```

`LogController` と `LogStream` は同じ `LogController` インスタンスを共有します。
`LogController` は `tail()`、`dates()`、`exists()` の通常 RPC を担当し、
`LogStream` は `read()` の server-streaming を担当します。両者自身に独立した
start/stop はなく、ライフサイクルは外側の gRPC server が管理します。

## クライアント

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

### API

```python
log.read()
log.read(date="2026-09-24")

log.tail(lines=100)
log.tail(lines=100, date="2026-09-24")

log.dates()

log.exists()
log.exists(date="2026-09-24")
```

## Python バージョン

公開コードの型アノテーションは Python 3.5 形式の `typing` 記法を使用しています。
f-string を使用しているため、実際の最低実行バージョンは Python 3.6 です。

## ドキュメント

Sphinx ドキュメントは `docs/` にあります。

```bash
cd docs
bash build.sh
```

GitHub Pages 用 workflow は配布 ZIP 内では `github/workflows/pages.yml` として
収録しています。リポジトリへ配置するときは `github` を `.github` に変更してください。

## テスト

```bash
python -m pytest
```

## License

`LICENSE` を参照してください。
