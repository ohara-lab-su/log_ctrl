# Quick Start

## 1. ログディレクトリを確認する

たとえばログディレクトリが次の状態だとします。

``` text
C:\opt\ese774\log\
├── cobotta3_server2.log
├── cobotta3_server2.log.2026-02-19
├── cobotta4_server.log
├── cobotta4_server.log.2026-04-06
├── cobotta4_server2.log
└── cobotta4_server2.log.2026-06-16
```

現在ログは、

``` text
<log_name>.log
```

ローテーション済みログは、

``` text
<log_name>.log.YYYY-MM-DD
```

です。

## 2. LogServer を起動する

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

`LOG_DIR`
は実際に存在するログディレクトリを指定します。存在しない場合、`LogCtrl`
の生成時に `NotADirectoryError` になります。

## 3. クライアントを作成する

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

`"log"` は `log_ctrl.server_grpc` が `register_device_proxy()`
で登録している DeviceProxy 名です。

## 4. まず `log_name` 一覧を取得する

特定のログ名をコードへ固定するのではなく、最初にサーバー上に実在するログを確認できます。

``` python
log_names = client.log_names()
print(log_names)
```

例:

``` text
[
    "cobotta3_server2",
    "cobotta4_server",
    "cobotta4_server2",
]
```

## 5. 日付一覧を取得する

``` python
log_name = log_names[0]

dates = client.dates(log_name)
print(dates)
```

`dates()` は実在する `<log_name>.log.YYYY-MM-DD`
の日付だけを返します。現在の `<log_name>.log` は日付一覧には入りません。

## 6. 現在ログを取得する

`log_names()` には、ローテーション済みファイルしか残っていない
`log_name` も含まれる可能性があります。現在ログを読む場合は `exists()`
で確認できます。

``` python
if client.exists(log_name):
    data = client.read(log_name)
    print("bytes:", len(data))
```

`read()` の戻り値は `bytes` です。

文字列として扱う場合:

``` python
text = data.decode("utf-8")
print(text)
```

## 7. ローテーション済みログを取得する

``` python
dates = client.dates(log_name)

if len(dates) > 0:
    date = dates[0]

    data = client.read(
        log_name,
        date=date,
    )

    print("date:", date)
    print("bytes:", len(data))
```

`dates()` は新しい日付から順に返します。そのため `dates[0]`
が一覧中の最新日付です。

## 8. トラブル調査用に実ファイル一覧を見る

``` python
files = client.raw_files()
print(files)
```

`raw_files()` はログとして解析できるファイルだけに限定せず、`log_dir`
以下に存在する全ファイルを相対パスで返します。

必要なら、その相対パスをそのまま `read_raw()` へ渡せます。

``` python
data = client.read_raw(
    "cobotta4_server.log.2026-04-06"
)
```

## 9. 終了する

``` python
client.close()
```

通常は `try` / `finally` で確実に閉じます。

``` python
try:
    print(client.log_names())
finally:
    client.close()
```
