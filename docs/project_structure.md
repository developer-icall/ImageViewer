# ImageViewer プロジェクト構造

## 概要

ImageViewerプロジェクトは、AI生成画像を表示・管理するためのWebアプリケーションです。このドキュメントでは、プロジェクト全体のフォルダ構造について説明します。

## プロジェクト全体の構造

```
ImageViewer/
├── imageviewer/           # メインアプリケーションディレクトリ
│   ├── static/            # フロントエンド用ファイル（ブラウザに送るファイル）
│   │   ├── sync_images/   # AI生成画像フォルダ
│   │   ├── css/           # スタイルシート
│   │   │   └── customize.scss  # SCSSファイル
│   │   └── ui_images/     # UI用の画像
│   ├── templates/         # テンプレートファイル
│   ├── tests/             # テスト関連ファイル
│   ├── logs/              # ログファイル
│   ├── config/            # 設定ファイルと関連プログラム
│   ├── app.py             # メインアプリケーションファイル
│   ├── sitemap.xml        # サイトマップ
│   └── __init__.py        # パッケージ初期化ファイル
├── docs/                  # ドキュメント
│   ├── folder_structure.md # 生成画像フォルダ構造の詳細説明
│   └── project_structure.md # このファイル（プロジェクト構造の説明）
├── tests/                 # プロジェクトレベルのテスト
├── logs/                  # プロジェクトレベルのログ
├── cache/                 # キャッシュファイル
├── feature/               # 機能関連ファイル
├── pyproject.toml         # Poetry設定ファイル
├── poetry.lock            # Poetryロックファイル
├── poetry.toml            # Poetry追加設定
└── README.md              # プロジェクト説明
```

## 主要ディレクトリとファイルの説明

### imageviewer/

メインアプリケーションのコードが格納されているディレクトリです。

- **static/**: フロントエンド用のファイルを格納
  - **sync_images/**: AI生成画像を格納（詳細は `folder_structure.md` を参照）
  - **css/**: スタイルシートファイル
  - **ui_images/**: UI用の画像ファイル

- **templates/**: Flaskテンプレートファイル

- **tests/**: アプリケーションレベルのテストコード

- **logs/**: アプリケーションログ

- **config/**: 設定ファイルと関連プログラム

- **app.py**: メインアプリケーションファイル（アプリ設定・定数などがまとまった根幹となるファイル）

- **sitemap.xml**: サイトマップファイル

- **__init__.py**: Pythonパッケージ初期化ファイル

### docs/

プロジェクトに関するドキュメントを格納するディレクトリです。

- **folder_structure.md**: 生成画像フォルダの詳細な構造を説明
- **project_structure.md**: このファイル（プロジェクト全体の構造を説明）

### その他のディレクトリとファイル

- **tests/**: プロジェクトレベルのテスト

- **logs/**: プロジェクトレベルのログ

- **cache/**: キャッシュファイル

- **feature/**: 機能関連ファイル

- **pyproject.toml**, **poetry.lock**, **poetry.toml**: Poetry（Pythonパッケージ管理ツール）の設定ファイル

- **README.md**: プロジェクトの概要、インストール手順、使用方法などを説明

## 生成画像フォルダ構造

AI生成画像のフォルダ構造については、`docs/folder_structure.md` を参照してください。