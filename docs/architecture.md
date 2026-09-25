# Architecture

## DeviceServer と LogServer

DeviceServer と LogServer は独立しています。DeviceServer にログ取得 RPC を追加しません。

```text
┌──────────────────────┐
│ DeviceServer         │
│  Device              │
│    ↓                 │
│  x_logger            │
└──────────┬───────────┘
           │ write
           ▼
     rotating log files
           ▲
           │ read only
┌──────────┴───────────┐
│ LogServer            │
│  LogController       │
│  LogStream           │
└──────────┬───────────┘
           │ gRPC
           ▼
       LogProxy
```

## LogController

`LogController` は短い応答を通常 RPC として扱います。

- `tail()`
- `dates()`
- `exists()`

ログディレクトリ、suffix、encoding を保持し、ログパスの解決も担当します。

## LogStream

`LogStream` はログ全文の `read()` を担当します。大きなログを単一 gRPC message に
詰め込まず、一定サイズの文字列チャンクとして server-streaming します。

`LogStream` は独自のログ設定を持たず、サーバー生成時に作られた
**同一の `LogController` インスタンス**を参照します。

## ライフサイクル

`LogController` と `LogStream` はそれぞれ start/stop しません。両者は RPC の処理
オブジェクトです。通信サーバーのライフサイクルは `create_grpc_server()` が返す
gRPC server が管理します。

```python
server = create_log_grpc_server(...)
server.add_insecure_port("[::]:50060")
server.start()
server.wait_for_termination()
```
