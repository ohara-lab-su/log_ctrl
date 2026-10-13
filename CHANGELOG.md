# CHANGELOG

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/log_ctrl/blob/main/CHANGELOG.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/log_ctrl/blob/main/CHANGELOG.md)

## v0.0.1

PyPI 公開準備。

### 変更内容

- PyPI 公開に向けたパッケージ公開準備。
- 英語版 README (`README.en.md`) を追加。
- CHANGELOG を追加。
- 日本語版 CHANGELOG (`CHANGELOG.md`) と英語版 CHANGELOG (`CHANGELOG.en.md`) を用意。

機能面の変更はありません。

## v0.0.0

初期バージョン。

### 実装内容

- `LogCtrl` によるログディレクトリの読み取り専用参照。
- 現在ログおよびローテーション済みログの `log_name` 一覧取得。
- 指定した `log_name` のローテーション日付一覧取得。
- 現在ログおよび日付指定ログの存在確認。
- ログ末尾を取得する `tail()`。
- ログディレクトリ以下のファイルを相対パスで列挙する `raw_files()`。
- ログファイルを `bytes` で取得する `read()`。
- 相対パスを指定してファイルを `bytes` で取得する `read_raw()`。
- ログディレクトリ外へのアクセスを防止するパス検証。
- `grpc_frame` を利用した独立したログ gRPC サーバー。
- `StreamCall` を利用したログファイルのチャンク転送。
- 同期 gRPC クライアント `SyncLogGrpcClient`。
- 非同期 gRPC クライアント `AsyncLogGrpcClient`。
