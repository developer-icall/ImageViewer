# 生成画像フォルダ仕様

このドキュメントでは、生成された画像のフォルダ構造について説明します。

## 生成時に動的に作成されるフォルダ

画像生成時には大項目・中項目・小項目に応じたフォルダの下に、作成日時と生成された画像の Seed 値を含むフォルダが作成されています。
それらのフォルダ構成に基づいて ImageViewer にて画像を一覧表示します

例）
```
imageviewer/static/sync_images/realistic/female/normal/20250221-12-2934224203/
```

フォルダ名の形式は以下の通りです：
- `YYYYMMDD-HH-SEEDVALUE`
  - `YYYYMMDD`: 年月日
  - `HH`: 時間
  - `SEEDVALUE`: 生成に使用されたSeed値

# 画像フォルダ構造パターン

- 基本構造は以下
    - imageviewer/static/sync_images/<style>/<category>/<subcategory>

# 具体的なフォルダ構造イメージ

## 大項目（スタイル）
/static/sync_images/realistic      # リアルテイスト
/static/sync_images/illustration   # イラストテイスト

## 中項目（カテゴリー）
/static/sync_images/<style>/female      # 女性
/static/sync_images/<style>/male        # 男性
/static/sync_images/<style>/animal      # 動物
/static/sync_images/<style>/background  # 背景
/static/sync_images/<style>/rpg_icon    # RPGアイコン
/static/sync_images/<style>/vehicle     # 乗り物

## 小項目（サブカテゴリー）
### 人物（female, male）
/static/sync_images/<style>/<category>/normal      # 通常
/static/sync_images/<style>/<category>/transparent # 透過
/static/sync_images/<style>/<category>/selfie      # セルフィー

### 動物（animal）
/static/sync_images/<style>/animal/dog    # 犬
/static/sync_images/<style>/animal/cat    # 猫
/static/sync_images/<style>/animal/bird   # 鳥
/static/sync_images/<style>/animal/fish   # 魚
/static/sync_images/<style>/animal/other  # その他

### 背景（background）
/static/sync_images/<style>/background/nature  # 自然
/static/sync_images/<style>/background/city    # 都市
/static/sync_images/<style>/background/sea     # 海
/static/sync_images/<style>/background/sky     # 空
/static/sync_images/<style>/background/other   # その他

### RPGアイコン（rpg_icon）
/static/sync_images/<style>/rpg_icon/weapon   # 武器・防具
/static/sync_images/<style>/rpg_icon/monster  # モンスター
/static/sync_images/<style>/rpg_icon/other    # その他

### 乗り物（vehicle）
/static/sync_images/<style>/vehicle/car       # 車
/static/sync_images/<style>/vehicle/ship      # 船
/static/sync_images/<style>/vehicle/airplane  # 飛行機
/static/sync_images/<style>/vehicle/other     # その他

## サムネイル・サンプル画像
各フォルダ内に以下のサブフォルダを配置：
/thumbnail           # サムネイル画像
/sample             # サンプル画像（透かし入り）
/sample-thumbnail   # サンプルサムネイル画像（透かし入り）
/half-resolution    # 半分の解像度の画像


## サブフォルダ構造

生成時に動的に作成されるフォルダ内には以下のサブフォルダが作成され、それぞれの仕様に応じた画像が保存されます。

```
/thumbnail          # サムネイル画像
/sample             # サンプル画像（透かし入り）
/sample-thumbnail   # サンプルサムネイル画像（透かし入り）
/half-resolution    # 半分の解像度の画像
```

### サブフォルダの役割

- **thumbnail**: 元画像のサムネイル版（小さいサイズ）
- **sample**: 透かし入りのサンプル画像（配布用）
- **sample-thumbnail**: 透かし入りのサンプル画像のサムネイル版
- **half-resolution**: 元画像の半分の解像度の画像（軽量版）

## 出力ディレクトリ構造の例

以下は、実際の出力ディレクトリ構造の例です：

```
imageviewer/static/sync_images/
├── realistic/
│   ├── female/
│   │   ├── normal/
│   │   │   ├── 20250221-12-2934224203/
│   │   │   │   ├── 00001.png                # 元画像
│   │   │   │   ├── thumbnail/
│   │   │   │   │   └── 00001.png            # サムネイル画像
│   │   │   │   ├── sample/
│   │   │   │   │   └── 00001.png            # サンプル画像（透かし入り）
│   │   │   │   ├── sample-thumbnail/
│   │   │   │   │   └── 00001.png            # サンプルサムネイル画像
│   │   │   │   └── half-resolution/
│   │   │   │       └── 00001.png            # 半分の解像度の画像
│   │   │   └── 20250221-13-3847583921/
│   │   │       └── ...
│   │   ├── selfie/
│   │   │   └── ...
│   │   └── transparent/
│   │       └── ...
│   └── male/
│       └── ...
└── illustration/
    └── ...
```