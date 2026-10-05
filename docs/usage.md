# Usage

## サーバー

公開されているサーバー起動関数は
`log_ctrl.server_grpc.log_grpc_server()` です。

``` python
from log_ctrl.server_grpc import log_grpc_server

log_grpc_server(
    grpc_host="0.0.0.0",
    grpc_port=50060,
    log_dir=r"C:\opt\ese774\log",
    encoding="utf-8",
    chunk_size=256 * 1024,
)
```

### `grpc_host`

gRPC server のbind先です。

### `grpc_port`

gRPC server のポート番号です。

### `log_dir`

参照対象のログディレクトリです。

`LogCtrl` の生成時に存在確認され、ディレクトリが存在しなければ
`NotADirectoryError` になります。

### `encoding`

`tail()` がファイル内容を `str` へ変換するときに使用する文字コードです。

`read()` / `read_raw()` はファイルをバイナリで転送するため、戻り値は
`bytes` です。

### `chunk_size`

`read()` / `read_raw()` の server-streaming
で1チャンクとして読み込むバイト数です。

既定値:

``` text
256 * 1024 bytes
```

大きなログファイルを単一のgRPCメッセージとして送信せず、複数チャンクに分割するために使用します。

### `logger` / `log_level`

`logger` を渡した場合はそのloggerを使用します。`logger=None`
の場合は標準の `logging` を使用します。

## DeviceProxy

同期クライアント:

``` python
from log_ctrl.server_grpc import DeviceProxy

client = DeviceProxy(
    "log",
    server_ip="127.0.0.1",
    server_port=50060,
    set_timeout_sec=10.0,
    async_mode=False,
)
```

`DeviceProxy("log", ...)` は登録済みの `SyncLogGrpcClient` または
`AsyncLogGrpcClient` を生成します。

## `log_names()`

``` python
log_names = client.log_names()
```

戻り値:

``` text
List[str]
```

`*.log` および `*.log.YYYY-MM-DD` から抽出した `log_name`
を重複なしで返します。戻り値は名前順です。

## `dates(log_name)`

``` python
dates = client.dates(
    "cobotta4_server"
)
```

戻り値:

``` text
List[str]
```

実在するローテーション済みログの日付を、新しい日付から順に返します。

## `exists(log_name, date=None)`

現在ログ:

``` python
exists = client.exists(
    "cobotta4_server"
)
```

指定日:

``` python
exists = client.exists(
    "cobotta4_server",
    date="2026-04-06",
)
```

戻り値は `bool` です。

## `tail(log_name, lines=100, date=None)`

現在ログ:

``` python
text = client.tail(
    "cobotta4_server",
    lines=100,
)
```

指定日:

``` python
text = client.tail(
    "cobotta4_server",
    lines=100,
    date="2026-04-06",
)
```

戻り値は `str` です。

`lines` は正の整数でなければなりません。

## `raw_files()`

``` python
files = client.raw_files()
```

戻り値:

``` text
List[str]
```

`log_dir` 以下を再帰的に走査し、全ファイルの相対パスを返します。

これはログ名解析用ではなく、実際にディレクトリ以下に何が存在するかを確認するトラブル調査用APIです。

## `read(log_name, date=None)`

現在ログ:

``` python
data = client.read(
    "cobotta4_server"
)
```

指定日:

``` python
data = client.read(
    "cobotta4_server",
    date="2026-04-06",
)
```

戻り値は `bytes` です。

内部では `grpc_frame` の `StreamCall`
でファイルをチャンク転送し、デバイス固有clientが受信したチャンクを結合します。

文字列へ変換する場合:

``` python
text = data.decode("utf-8")
```

## `read_raw(relative_path)`

``` python
data = client.read_raw(
    "cobotta4_server.log.2026-04-06"
)
```

`raw_files()` で得られる相対パスを指定してファイル本体を取得できます。

サブディレクトリ内のファイルも相対パスで指定できますが、`log_dir`
外へ出るパスは拒否されます。

戻り値は `bytes` です。

## クライアント終了

``` python
client.close()
```

`grpc_frame` のchannelを閉じます。

## 非同期クライアント

``` python
client = DeviceProxy(
    "log",
    server_ip="127.0.0.1",
    server_port=50060,
    set_timeout_sec=10.0,
    async_mode=True,
)
```

`AsyncLogGrpcClient` では `read()` と `read_raw()` も `await`
して使用します。

``` python
data = await client.read(
    "cobotta4_server"
)
```

通常RPCとして自動bindされるメソッドについても、`grpc_frame`
の非同期client APIに従って使用します。
