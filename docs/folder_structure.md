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
│   │   │   ├── 20231124-17-173219185/  # 画像生成日-連番-シード値
│   │   │   │   ├── 00000-173219185.png # 元画像
│   │   │   │   ├── 00000-173219185.jpg # JPG形式の元画像
│   │   │   │   ├── 00000-173219185.json # プロンプト情報
│   │   │   │   ├── sample/              # サンプル画像（透かし入り）
│   │   │   │   ├── thumbnail/           # サムネイル画像
│   │   │   │   ├── sample-thumbnail/    # サンプルサムネイル画像
│   │   │   │   └── half-resolution/     # 半分解像度画像
│   │   │   └── ...                      # 他の生成日フォルダ
│   │   ├── transparent/                # 透過サブカテゴリ
│   │   │   └── ...                      # 生成日フォルダ
│   │   └── selfie/                     # 自撮りサブカテゴリ
│   │       └── ...                      # 生成日フォルダ
│   ├── male/                           # 男性カテゴリ
│   │   ├── normal/                     # 通常サブカテゴリ
│   │   ├── transparent/                # 透過サブカテゴリ
│   │   └── selfie/                     # 自撮りサブカテゴリ
│   ├── animal/                         # 動物カテゴリ
│   │   ├── dog/                        # 犬サブカテゴリ
│   │   ├── cat/                        # 猫サブカテゴリ
│   │   ├── bird/                       # 鳥サブカテゴリ
│   │   ├── fish/                       # 魚サブカテゴリ
│   │   └── other/                      # その他の動物サブカテゴリ
│   ├── vehicle/                        # 乗り物カテゴリ
│   │   ├── car/                        # 車サブカテゴリ
│   │   ├── motorcycle/                 # バイクサブカテゴリ
│   │   ├── airplane/                   # 飛行機サブカテゴリ
│   │   ├── ship/                       # 船サブカテゴリ
│   │   └── other/                      # その他の乗り物サブカテゴリ
│   ├── background/                     # 背景カテゴリ
│   │   ├── nature/                     # 自然サブカテゴリ
│   │   ├── city/                       # 都市サブカテゴリ
│   │   ├── house/                      # 家サブカテゴリ
│   │   ├── sky/                        # 空サブカテゴリ
│   │   ├── sea/                        # 海サブカテゴリ
│   │   └── other/                      # その他の背景サブカテゴリ
│   └── .gitkeep                        # Gitリポジトリ用の空ファイル
└── illustration/                       # イラスト画像スタイル
    ├── female/                         # 女性カテゴリ
    │   ├── normal/                     # 通常サブカテゴリ
    │   ├── transparent/                # 透過サブカテゴリ
    │   └── selfie/                     # 自撮りサブカテゴリ
    ├── male/                           # 男性カテゴリ
    │   ├── normal/                     # 通常サブカテゴリ
    │   ├── transparent/                # 透過サブカテゴリ
    │   └── selfie/                     # 自撮りサブカテゴリ
    ├── animal/                         # 動物カテゴリ
    │   ├── dog/                        # 犬サブカテゴリ
    │   ├── cat/                        # 猫サブカテゴリ
    │   ├── bird/                       # 鳥サブカテゴリ
    │   ├── fish/                       # 魚サブカテゴリ
    │   └── other/                      # その他の動物サブカテゴリ
    ├── vehicle/                        # 乗り物カテゴリ
    │   ├── car/                        # 車サブカテゴリ
    │   ├── motorcycle/                 # バイクサブカテゴリ
    │   ├── airplane/                   # 飛行機サブカテゴリ
    │   ├── ship/                       # 船サブカテゴリ
    │   └── other/                      # その他の乗り物サブカテゴリ
    ├── background/                     # 背景カテゴリ
    │   ├── nature/                     # 自然サブカテゴリ
    │   ├── city/                       # 都市サブカテゴリ
    │   ├── house/                      # 家サブカテゴリ
    │   ├── sky/                        # 空サブカテゴリ
    │   ├── sea/                        # 海サブカテゴリ
    │   └── other/                      # その他の背景サブカテゴリ
    ├── rpg_icon/                       # RPGアイコンカテゴリ
    │   ├── monster/                    # モンスターサブカテゴリ
    │   ├── weapon/                     # 武器サブカテゴリ
    │   └── other/                      # その他のRPGアイコンサブカテゴリ
    ├── other/                          # その他カテゴリ
    └── .gitkeep                        # Gitリポジトリ用の空ファイル
```

## フォルダ名の形式

生成時に動的に作成されるフォルダ名の形式は以下の通りです：
- `YYYYMMDD-HH-SEEDVALUE`
  - YYYYMMDD: 画像生成日（年月日）
  - HH: 生成時の時間
  - SEEDVALUE: 生成に使用されたシード値

## 画像ファイル名の形式

各画像ファイル名の形式は以下の通りです：
- `NNNNN-SEEDVALUE.png/jpg`
  - NNNNN: 連番（00000 または 00001 から始まる）
  - SEEDVALUE: 生成に使用されたシード値

## 特別なファイル

- `NNNNN-SEEDVALUE.json`: 対応する画像の生成に使用されたプロンプト情報が含まれるJSONファイル
