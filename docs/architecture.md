# Architecture

## 全体構成

`log_ctrl` はログを書き込むプロセスとは独立しています。

``` text
┌───────────────────────────┐
│ application / DeviceServer│
│ logger                    │
└─────────────┬─────────────┘
              │ write
              ▼
       log directory
              ▲
              │ read only
              │
┌─────────────┴─────────────┐
│ log_ctrl                  │
│                           │
│ LogCtrl                   │
│   ├─ log_names()          │
│   ├─ dates()              │
│   ├─ raw_files()          │
│   ├─ exists()             │
│   └─ tail()               │
│                           │
│ _LogStream                │
│   ├─ read()               │
│   └─ read_raw()           │
└─────────────┬─────────────┘
              │
              │ grpc_frame
              ▼
┌───────────────────────────┐
│ DeviceProxy("log")        │
│                           │
│ SyncLogGrpcClient         │
│ AsyncLogGrpcClient        │
└───────────────────────────┘
```

ログを書き込む側に `log_ctrl` 固有RPCを追加する必要はありません。

## `LogCtrl`

`LogCtrl` はログディレクトリをローカルに扱う制御クラスです。

保持する主な状態は、

-   `log_dir`
-   `encoding`

です。

生成時に `log_dir` を `Path.resolve()`
し、実在するディレクトリであることを確認します。

### 通常RPCとして公開されるメソッド

``` text
log_names()
dates(log_name)
raw_files()
exists(log_name, date=None)
tail(log_name, lines=100, date=None)
```

これらは `grpc_frame`
のDescribe/Call機構によってクライアントへbindされます。

`LogCtrl` は gRPC
固有処理を持たず、ローカルクラスとしてファイル探索・検証・末尾読み込みを担当します。

## `log_names()`

`log_dir` 直下のファイルについて、

``` text
<log_name>.log
<log_name>.log.YYYY-MM-DD
```

を解析し、`log_name` の集合を作ります。

現在ログと履歴ログのどちらからでも名前を検出するため、現在の `.log`
ファイルが存在しない名前も返ることがあります。

## `dates()`

指定された `log_name` に対して、

``` text
<log_name>.log.YYYY-MM-DD
```

に一致する実在ファイルを調べます。

suffixは `datetime.strptime(..., "%Y-%m-%d")`
で検証され、新しい日付から順に返されます。

## `raw_files()`

`Path.rglob("*")` によって `log_dir` 以下を再帰的に走査します。

ログ命名規則によるフィルタは行わず、全ファイルを `log_dir`
からの相対パスとして返します。

これは通常のログ探索とは別に、トラブル時に実ファイル構成を確認するための経路です。

## `_LogStream`

ファイル本体は通常RPCの戻り値として一括送信せず、`grpc_frame` の
`StreamCall` を使用します。

ストリーム側には、

``` text
read(log_name, date=None)
read_raw(relative_path)
```

があります。

`read()` は `LogCtrl` のログパス解決を使用し、`read_raw()`
はraw相対パス解決を使用します。

ファイルは `chunk_size` ごとにバイナリで読み、

``` text
bytes
bytes
bytes
...
```

として順次yieldします。

## クライアント側

`log_ctrl.server_grpc` のimport時に、

``` python
register_device_proxy(
    "log",
    async_client_cls=AsyncLogGrpcClient,
    sync_client_cls=SyncLogGrpcClient,
    ...
)
```

によって `DeviceProxy` へログclientを登録します。

利用側は、

``` python
client = DeviceProxy(
    "log",
    server_ip="127.0.0.1",
    server_port=50060,
    async_mode=False,
)
```

とするだけで、ログ用clientを取得できます。

### 通常RPC

`log_names()`、`dates()`、`raw_files()`、`exists()`、`tail()` は
`grpc_frame` が `LogCtrl` のDescribe情報から透過的にbindします。

### ファイル本体

`read()` / `read_raw()` はデバイス固有client側で実装されています。

同期clientでは `stream_call()` を反復してチャンクを `bytearray`
に結合し、最終的に `bytes` を返します。

そのためアプリケーション側は `StreamCall` やチャンク境界を意識しません。

## パス解決

通常ログのパスは、

``` text
log_name
    ↓
<log_name>.log
```

または、

``` text
log_name + date
    ↓
<log_name>.log.YYYY-MM-DD
```

として解決されます。

`log_name` にディレクトリ成分や `.log` を含める指定は拒否されます。

`read_raw()` 用の相対パスは、`log_dir` と結合して `resolve()`
した後、解決結果が `log_dir` 内にあることを確認します。これにより `../`
などによるログディレクトリ外へのアクセスを防ぎます。

## ライフサイクル

サーバー起動関数 `log_grpc_server()` が、

1.  `LogCtrl` を生成
2.  ストリーム処理オブジェクトを生成
3.  `grpc_frame` のgRPC serverを生成
4.  指定host/portへbind
5.  serverをstart
6.  自己接続による起動確認
7.  終了まで待機

というライフサイクルを管理します。

クライアント側は `DeviceProxy` で生成し、使用後に、

``` python
client.close()
```

でchannelを閉じます。
