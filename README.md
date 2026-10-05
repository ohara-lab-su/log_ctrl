# log_ctrl

`log_ctrl`
は、指定したログディレクトリに保存されているログファイルを、`grpc_frame`
を使ってネットワーク越しに参照するためのパッケージです。

ログを書き込む側の DeviceServer やアプリケーションにはログ取得 RPC
を追加しません。`log_ctrl` は既存のログファイルを read-only
で参照する独立した gRPC サーバーとして動作します。

``` text
application / DeviceServer
        │
        │ write
        ▼
C:\opt\ese774\log
├── cobotta4_server.log
├── cobotta4_server.log.2026-04-06
├── cobotta4_server2.log
└── cobotta4_server2.log.2026-06-16
        ▲
        │ read only
        │
     LogCtrl
        │
        ▼
 log gRPC server
        │
        ▼
DeviceProxy("log", ...)
```

## ログ名

`log_ctrl` では、`.log` より前の部分を `log_name` と呼びます。

``` text
cobotta4_server.log
^^^^^^^^^^^^^^^
   log_name
```

ローテーション済みログは次の形式です。

``` text
<log_name>.log.YYYY-MM-DD
```

`log_name` は DeviceServer
名やデバイスクラス名と一致する必要はありません。`log_ctrl`
はファイル名として存在する `log_name` をそのまま扱います。

## 主な機能

-   `log_names()` : 実在するログファイルから `log_name` 一覧を取得
-   `dates(log_name)` : 指定した `log_name`
    のローテーション日付一覧を取得
-   `exists(log_name, date=None)` : 現在ログまたは指定日ログの存在確認
-   `tail(log_name, lines=100, date=None)` : ログ末尾を文字列で取得
-   `raw_files()` : ログディレクトリ以下の全ファイルを相対パスで列挙
-   `read(log_name, date=None)` : ログファイル本体を `bytes` で取得
-   `read_raw(relative_path)` : `raw_files()` で確認した任意ファイルを
    `bytes` で取得

大きなログファイルは `grpc_frame` の `StreamCall`
を使ってチャンク転送します。利用側ではストリーム処理を直接扱う必要はなく、`read()`
/ `read_raw()` が受信したチャンクを結合して `bytes` として返します。

## インストール

`grpc_frame` を利用可能な環境でインストールします。

``` bash
python -m pip install .
```

開発時は次のように editable install できます。

``` bash
python -m pip install -e .
```

## LogServer の起動

``` python
from log_ctrl.server_grpc import log_grpc_server

GRPC_HOST = "0.0.0.0"
GRPC_PORT = 50060
LOG_DIR = r"C:\opt\ese774\log"

log_grpc_server(
    grpc_host=GRPC_HOST,
    grpc_port=GRPC_PORT,
    log_dir=LOG_DIR,
)
```

`logger` を省略した場合は標準の `logging` が使用されます。既存の logger
を使用する場合は `logger=` で渡せます。

## クライアント

`grpc_frame` の透過クライアントとして `DeviceProxy` を使用します。

``` python
from log_ctrl.server_grpc import DeviceProxy

client = DeviceProxy(
    "log",
    server_ip="127.0.0.1",
    server_port=50060,
    set_timeout_sec=10.0,
    async_mode=False,
)

try:
    log_names = client.log_names()
    print(log_names)

    if len(log_names) > 0:
        log_name = log_names[0]

        print(client.dates(log_name))

        if client.exists(log_name):
            data = client.read(log_name)
            print(len(data))

finally:
    client.close()
```

`log_names()` で返される名前は、現在の `<log_name>.log`
が存在する名前だけとは限りません。ローテーション済みファイルだけが残っている場合も一覧に含まれます。現在ログを読む前に必要に応じて
`exists(log_name)` を確認してください。

## API

``` python
client.log_names()
client.dates(log_name)

client.exists(log_name)
client.exists(log_name, date="2026-04-06")

client.tail(log_name, lines=100)
client.tail(log_name, lines=100, date="2026-04-06")

client.raw_files()

client.read(log_name)
client.read(log_name, date="2026-04-06")

client.read_raw("cobotta4_server.log.2026-04-06")
```

`read()` と `read_raw()` の戻り値は `bytes`
です。ログを文字列として扱う場合は、使用している文字コードに合わせてクライアント側で
decode します。

``` python
text = client.read(log_name).decode("utf-8")
```

`tail()` はサーバー側で設定された `encoding` を使って decode され、`str`
を返します。

## ドキュメント

Sphinx 用文書は `docs/` にあります。

-   `docs/index.md`
-   `docs/quickstart.md`
-   `docs/usage.md`
-   `docs/rotation.md`
-   `docs/architecture.md`

## License

`LICENSE` を参照してください。
