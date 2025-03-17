# プロジェクトフォルダ構成

## 基本構造

```
ImageViewer/
├── imageviewer/           # メインアプリケーションディレクトリ
│   ├── static/            # フロントエンド用ファイル（ブラウザに送るファイル）
│   ├── tests/             # テスト関連ファイル
│   ├── logs/              # ログファイル
│   ├── config/            # 設定ファイルと関連プログラム
│   ├── templates/         # テンプレートファイル
│   ├── app.py             # メインアプリケーションファイル
│   ├── sitemap.xml        # サイトマップ
│   └── __init__.py        # パッケージ初期化ファイル
├── docs/                  # ドキュメント
├── tests/                 # プロジェクトレベルのテスト
├── logs/                  # プロジェクトレベルのログ
├── cache/                 # キャッシュファイル
├── feature/               # 機能関連ファイル
├── pyproject.toml         # Poetry設定ファイル
├── poetry.lock            # Poetryロックファイル
├── poetry.toml            # Poetry追加設定
└── README.md              # プロジェクト説明
```

## 詳細なフォルダ構造

```
ImageViewer/                           # プロジェクトルート
├── imageviewer/                       # メインアプリケーションディレクトリ
│   ├── static/                        # フロントエンド用ファイル（ブラウザに送るファイル）
│   │   ├── sync_images/               # AI生成画像フォルダ
│   │   ├── css/                       # スタイルシート
│   │   ├── js/                        # JavaScriptファイル
│   │   ├── translate_json/            # プロンプト翻訳用JSONファイル
│   │   │   ├── pose.json              # ポーズ関連の翻訳
│   │   │   ├── Hair Color.json        # 髪の色関連の翻訳
│   │   │   ├── Cloth.json             # 衣服関連の翻訳
│   │   │   └── ...                    # その他の翻訳ファイル
│   │   └── ui_images/                 # UI用の画像
│   ├── tests/                         # テスト関連ファイル
│   ├── logs/                          # ログファイル
│   ├── cache/                         # キャッシュファイル
│   ├── feature/                       # 機能関連ファイル
│   ├── config/                        # 設定ファイルと関連プログラム
│   ├── templates/                     # テンプレートファイル
│   ├── app.py                         # メインアプリケーションファイル
│   ├── sitemap.xml                    # サイトマップ
│   └── __init__.py                    # パッケージ初期化ファイル
├── docs/                              # ドキュメント
├── tests/                             # プロジェクトレベルのテスト
├── logs/                              # プロジェクトレベルのログ
├── cache/                             # キャッシュファイル
├── feature/                           # 機能関連ファイル
├── pyproject.toml                     # Poetry設定ファイル
├── poetry.lock                        # Poetryロックファイル
├── poetry.toml                        # Poetry追加設定
└── README.md                          # プロジェクト説明
```

### AI生成画像フォルダ構造

AI生成画像は `imageviewer/static/sync_images` フォルダ以下に以下の構造で保存されます：

```
sync_images/                           # AI生成画像フォルダ
├── realistic/                         # リアルな画像スタイル
│   ├── female/                        # 女性カテゴリ
│   │   ├── normal/                    # 通常サブカテゴリ
│   │   │   ├── 20240101-01-1234567890/  # 画像生成日-連番-シード値
│   │   │   │   ├── 00000-1234567890.png # 元画像
│   │   │   │   ├── 00000-1234567890.json # プロンプト情報
│   │   │   │   ├── sample/              # サンプル画像（透かし入り）
│   │   │   │   ├── thumbnail/           # サムネイル画像
│   │   │   │   ├── sample-thumbnail/    # サンプルサムネイル画像
│   │   │   │   └── half-resolution/     # 半分解像度画像
│   │   │   └── ...
│   │   ├── transparent/                # 透過サブカテゴリ
│   │   └── ...
│   ├── male/                           # 男性カテゴリ
│   ├── animal/                         # 動物カテゴリ
│   └── ...
└── illustration/                       # イラスト画像スタイル
    └── ...
```

## フォルダ名の形式

生成時に動的に作成されるフォルダ名の形式は以下の通りです：
- `YYYYMMDD-HH-SEEDVALUE`