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

## 生成画像フォルダ構造

生成された画像は以下の構造で保存されます：

```
imageviewer/static/sync_images/
├── realistic/                                # リアルテイスト（大項目）
│   ├── female/                               # 女性（中項目）
│   │   ├── normal/                           # 通常（小項目）
│   │   │   ├── YYYYMMDD-HH-SEEDVALUE/        # 生成日時とSeed値
│   │   │   │   ├── 00001.png                 # 元画像
│   │   │   │   ├── thumbnail/                # サムネイル画像
│   │   │   │   │   └── 00001.png
│   │   │   │   ├── sample/                   # サンプル画像（透かし入り）
│   │   │   │   │   └── 00001.png
│   │   │   │   ├── sample-thumbnail/         # サンプルサムネイル画像
│   │   │   │   │   └── 00001.png
│   │   │   │   └── half-resolution/          # 半分の解像度の画像
│   │   │   │       └── 00001.png
│   │   │   └── ...
│   │   ├── transparent/                      # 透過
│   │   │   └── ...
│   │   └── selfie/                           # セルフィー
│   │       └── ...
│   ├── male/                                 # 男性
│   │   ├── normal/
│   │   ├── transparent/
│   │   └── selfie/
│   ├── animal/                               # 動物
│   │   ├── dog/                              # 犬
│   │   ├── cat/                              # 猫
│   │   ├── bird/                             # 鳥
│   │   ├── fish/                             # 魚
│   │   └── other/                            # その他
│   ├── background/                           # 背景
│   │   ├── nature/                           # 自然
│   │   ├── city/                             # 都市
│   │   ├── sea/                              # 海
│   │   ├── sky/                              # 空
│   │   └── other/                            # その他
│   ├── rpg_icon/                             # RPGアイコン
│   │   ├── weapon/                           # 武器・防具
│   │   ├── monster/                          # モンスター
│   │   └── other/                            # その他
│   └── vehicle/                              # 乗り物
│       ├── car/                              # 車
│       ├── ship/                             # 船
│       ├── airplane/                         # 飛行機
│       └── other/                            # その他
└── illustration/                             # イラストテイスト（大項目）
    ├── female/
    ├── male/
    ├── animal/
    ├── background/
    ├── rpg_icon/
    └── vehicle/
```

## フォルダ名の形式

生成時に動的に作成されるフォルダ名の形式は以下の通りです：
- `YYYYMMDD-HH-SEEDVALUE`
  - `YYYYMMDD`: 年月日
  - `HH`: 時間
  - `SEEDVALUE`: 生成に使用されたSeed値

例：`20250221-12-2934224203`

## サブフォルダの役割

各生成画像フォルダ内には以下のサブフォルダが作成されます：

- **thumbnail**: 元画像のサムネイル版（小さいサイズ）
- **sample**: 透かし入りのサンプル画像（配布用）
- **sample-thumbnail**: 透かし入りのサンプル画像のサムネイル版
- **half-resolution**: 元画像の半分の解像度の画像（軽量版）