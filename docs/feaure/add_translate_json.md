# 依頼内容

- `/ImageViewer/imageviewer/static/prompts` 以下の各スタイル/カテゴリ/サブカテゴリ内の各画像生成時に使用するプロンプトが記載されている「各画像生成時に使用するプロンプト設定ファイル」を順番に全て読み込み、`/ImageViewer/imageviewer/static/translate_json` フォルダ以下に追加が必要な項目があれば追加してください。ファイル自体存在しない場合は「英語-日本語変換表の json ファイル」を作成してから追加してください。
    - フォルダ構成やプロンプト設定ファイルの仕様は下記に「各画像生成時に使用するプロンプト設定ファイル仕様」として記載しているので参照してください
- `/ImageViewer/imageviewer/docs/translate_json_spec.md` の仕様を参照して、各画像生成時に使用されたプロンプトが記載されている json ファイルを使用して英語を日本語に変換している仕様を理解してください
- 「英語-日本語変換表の json ファイル」の名前には下記に記載のある「プロンプト分類名」が使用されます
- 「英語-日本語変換表の json ファイル」へ追加する必要があるのは `positive_base.json`, `positive_optional.json`, `positive_pose.json` に記載のあるものだけです。他のファイルは必要ありません

# 特記事項

- 翻訳の際に`詳細な`という文言は入れない
- 以下「プロンプト分類名」の場合「英語-日本語変換表の json ファイル」として作成しない
  - `Body Type`
  - `Base Positive Prompt`
  - `Must Positive Prompt`
  - `Display`
  - `Setting`

# 各画像生成時に使用するプロンプト設定ファイル仕様

## 1. フォルダ構成

```
ImageViewer/imageviewer/static/prompts/
├── [style]/
│   ├── [category]/
│   │   ├── [subcategory]/（必要に応じてサブカテゴリ以下に各プロンプト設定ファイルを配置）
│   │   ├── positive_base.json
│   │   ├── positive_optional.json
│   │   ├── positive_pose.json
│   │   ├── positive_selfie.json
│   │   ├── negative.json
│   │   ├── cancel_seeds.json
│   │   └── positive_cancel_pair.json
```

- **style**: 画像スタイル（例: realistic, illustration）
- **category**: カテゴリー（例: female, male, animal）
- **subcategory**: サブカテゴリー（必要に応じて）

## 2. プロンプト設定ファイルの基本構造

すべてのプロンプト設定ファイルは以下の基本構造に従います：

```json
{
  "プロンプト分類名": {
    "prompts": [
      "プロンプト1",
      "プロンプト2",
      "プロンプト3",
      ...
    ],
    "use_max_prompts": 数値,
    "use_min_prompts": 数値,
    "position": "start" または "end"  // オプション: プロンプトの配置位置
  },
  "別のプロンプト分類名": {
    ...
  }
}
```

- **プロンプト分類名**: 任意の名前（例: "Base Positive Prompt", "Hair Type"）
- **prompts**: 選択対象となるプロンプトの配列
- **use_max_prompts**: 最大選択数（この分類から最大何個のプロンプトを選ぶか）
- **use_min_prompts**: 最小選択数（この分類から最低何個のプロンプトを選ぶか）
- **position**: プロンプトの配置位置（オプション）
  - `"start"`: プロンプト文字列の先頭に配置
  - `"end"`: プロンプト文字列の末尾に配置
  - 指定なし: 通常の位置（他のプロンプトと混合）

### 選択ルール例

- `"use_max_prompts": 1, "use_min_prompts": 1` → 必ず1つだけ選択
- `"use_max_prompts": 2, "use_min_prompts": 0` → 0〜2個をランダムに選択
- `"use_max_prompts": 0, "use_min_prompts": 0` → 選択しない（オプション）

### 条件付きプロンプト

特定の条件が満たされた場合にのみプロンプトを選択するには、`condition`要素を追加します：

```json
{
  "特定条件付きプロンプト": {
    "prompts": [
      "条件付きプロンプト1",
      "条件付きプロンプト2",
      ...
    ],
    "use_max_prompts": 1,
    "use_min_prompts": 0,
    "position": "start",  // オプション: プロンプトの配置位置
    "condition": {
      "category": "Weapon Type",
      "contains": ["dagger"]
    }
  }
}
```

- **condition**: 条件を指定するオブジェクト
  - **category**: 条件をチェックするプロンプト分類名
  - **contains**: 指定した文字列が含まれているかをチェックする配列

この例では、「Weapon Type」カテゴリで選択されたプロンプトに「dagger」という文字列が含まれている場合にのみ、このプロンプト分類からプロンプトが選択されます。また、選択されたプロンプトはプロンプト文字列の先頭に配置されます。

## 3. 各プロンプト設定ファイルの役割

### 3.1 positive_base.json

基本となるプロンプト設定。同一人物の異なるバージョンを生成する際も、このプロンプトは固定されます。
同じ seed でかつ同じベースプロンプトを指定しつつ、後述の `positive_optional.json` や `positive_pose.json` で服装やポーズのプロンプトを指定することで、同じ人物の異なる服装・ポーズの画像を生成します。

**主な分類例**:
- **Base Positive Prompt**: 基本的な画質や人物の指定
- **Women/Men Type**: 人物タイプ（アイドル、モデルなど）
- **Body Type**: 体型の指定
- **Hair Type**: 髪型の指定
- **Hair Color**: 髪の色の指定

```json
{
  "Base Positive Prompt": {
    "prompts": ["(8k, RAW photo, best quality, masterpiece:1.2), (1girl:1.3), (looking at viewer:1.4)"],
    "use_max_prompts": 1,
    "use_min_prompts": 1
  },
  "Women Type": {
    "prompts": [
      "Famous Japanese Male Idols",
      "japanese cool men",
      "japanese men",
      "Male Athletes in Japan",
      "Japanese male fashion models",
      "Famous Korean Male Idols",
      "Korean cool men",
      "Korean men",
      "Male Athletes in Korean",
      "Korean male fashion models"
    ],
    "use_max_prompts": 1,
    "use_min_prompts": 1
  },
  "Weapon Type": {
    "prompts": [
      "(medieval sword:1.4)",
      "(iron dagger:1.4)",
      "(battle axe:1.4)"
    ],
    "use_max_prompts": 1,
    "use_min_prompts": 1,
    "position": "start"  // 武器タイプをプロンプトの先頭に配置
  }
}
```

### 3.2 positive_optional.json

オプション的なプロンプト設定。服装、アクセサリー、場所、構図などを指定します。

**主な分類例**:
- **Cloth**: 服装（ドレス、Tシャツなど）
- **Accessory**: アクセサリー（ネックレス、イヤリングなど）
- **Place**: 場所（部屋、ビーチなど）
- **composition**: 構図（顔アップ、上半身など）

### 3.3 positive_pose.json

ポーズや表情に関するプロンプト設定。

**主な分類例**:
- **pose**: 体のポーズ（座る、立つなど）
- **Face**: 表情（笑顔、真顔など）

### 3.4 positive_selfie.json

自撮り写真用のポーズ設定。`subcategory`が`selfie`の場合に`positive_pose.json`の代わりに使用されます。

**主な分類例**:
- **pose**: 自撮りポーズ（右手でセルフィー、両手でセルフィーなど）
- **Face**: 表情（笑顔など）


## 5. 使用例

リアルな女性の画像を生成する場合：

1. `positive_base.json`から基本的な人物設定（髪型、髪色など）を選択
2. `positive_optional.json`から服装、場所、構図などを選択
3. `positive_pose.json`または`positive_selfie.json`からポーズと表情を選択
4. `negative.json`から除外要素を適用
5. `positive_cancel_pair.json`を参照して不適切な組み合わせを除外
6. `cancel_seeds.json`を参照して使用しないseed値を除外

これらの設定を組み合わせることで、多様でありながらも自然な画像生成が可能になります。

RPGアイコンの武器を生成する場合：

1. `positive_base.json`から基本的な設定と武器タイプ（先頭に配置）を選択
2. `positive_optional.json`からエフェクトや表示設定を選択
3. `negative.json`から除外要素を適用
4. `positive_cancel_pair.json`を参照して矛盾する材質の組み合わせを除外

武器タイプを先頭に配置することで、より明確に指定された武器が生成されます。


# 関連ファイル, フォルダ

- `/ImageViewer/imageviewer/static/prompts`
- `/ImageViewer/imageviewer/static/translate_json`

---
以下のステップで進みたいですが、各ステップ毎に先へ進んでいいか確認してください

1. `/ImageViewer/imageviewer/static/prompts/realistic/female` フォルダ以下にあるプロンプトファイルについて作業をして
2. `/ImageViewer/imageviewer/static/prompts/realistic/male` フォルダ以下にあるプロンプトファイルについて作業をして
3. `/ImageViewer/imageviewer/static/prompts/illustration` フォルダ以下にあるプロンプトファイルについて作業をして

それではステップ1からお願いします
