# Rotation

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/log_ctrl/en/manual/rotation.html)  [![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/log_ctrl/ja/manual/rotation.html)


`log_ctrl` がログとして認識するファイル名は次の2形式です。

``` text
<log_name>.log
<log_name>.log.YYYY-MM-DD
```

例:

``` text
cobotta4_server.log
cobotta4_server.log.2026-03-31
cobotta4_server.log.2026-04-06
```

## 現在ログ

日付suffixを持たない、

``` text
<log_name>.log
```

が現在ログです。

現在ログには `current`
のような特別な日付名や仮想ファイル名はありません。

``` python
data = client.read("cobotta4_server")
```

は、

``` text
cobotta4_server.log
```

を読みます。

## ローテーション済みログ

``` python
data = client.read(
    "cobotta4_server",
    date="2026-04-06",
)
```

は、

``` text
cobotta4_server.log.2026-04-06
```

を読みます。

日付は厳密に `YYYY-MM-DD` 形式として検証されます。

## 日付一覧

``` python
dates = client.dates(
    "cobotta4_server"
)
```

`dates()` は、実際に存在する、

``` text
<log_name>.log.YYYY-MM-DD
```

を調べ、正しい日付suffixを持つファイルだけを返します。

戻り値は新しい日付から順にソートされます。

``` text
[
    "2026-04-06",
    "2026-03-31",
    "2026-03-30",
]
```

日付は連続しているとは限りません。存在しない日付を補完しません。

また、現在の `<log_name>.log` は `dates()` の戻り値には含まれません。

## `log_names()`

`log_names()` は、現在ログとローテーション済みログの両方から `log_name`
を抽出します。

したがって、

``` text
old_device.log.2026-02-19
```

だけが存在し、

``` text
old_device.log
```

が存在しない場合でも、

``` python
client.log_names()
```

には `"old_device"` が含まれます。

現在ログの有無は別途、

``` python
client.exists("old_device")
```

で確認できます。

## ローテーション管理の責務

`log_ctrl` 自身は、

-   ログの書き込み
-   ローテーション
-   保持世代数の管理
-   古いログの削除

を行いません。

これらはログを書き込む側の責務です。`log_ctrl`
はディレクトリに実在するファイルだけを参照します。

## 想定外ファイル

`log_names()` と `dates()`
は上記のログ命名規則に合うファイルだけを解析します。

一方、トラブル調査用の、

``` python
client.raw_files()
```

は命名規則でフィルタせず、`log_dir` 以下の全ファイルを返します。

そのため、ログ命名規則外のファイルでも、

``` python
client.read_raw(relative_path)
```

で内容を取得できます。

## パス制限

通常の `read()`、`tail()`、`exists()`、`dates()` では `log_name`
にパスを含めることはできません。また `log_name` 自体に `.log`
を含めることもできません。

`read_raw()` は相対パスを受け取りますが、解決後のパスが `log_dir`
の外へ出る指定は拒否されます。絶対パスも使用できません。
