# 依頼内容

- `/ImageViewer/imageviewer/static/prompts/illustration/rpg_icon/monster` 以下のillustration/rpg_icon/monster 内の各画像生成時に使用するプロンプトが記載されている「各画像生成時に使用するプロンプト設定ファイル」を順番に全て読み込み、`/ImageViewer/imageviewer/static/translate_json` フォルダ以下に追加が必要な項目があれば追加してください。ファイル自体存在しない場合は「英語-日本語変換表の json ファイル」を作成してから追加してください。
    - フォルダ構成やプロンプト設定ファイルの仕様は下記に「各画像生成時に使用するプロンプト設定ファイル仕様」として記載しているので参照してください
- `/ImageViewer/imageviewer/docs/translate_json_spec.md` の仕様を参照して、各画像生成時に使用されたプロンプトが記載されている json ファイルを使用して英語を日本語に変換している仕様を理解してください
- 「英語-日本語変換表の json ファイル」の名前には下記に記載のある「プロンプト分類名」が使用されます
- 「英語-日本語変換表の json ファイル」へ追加する必要があるのは `positive_base.json`, `positive_optional.json`, `positive_pose.json` に記載のあるものだけです。他のファイルは必要ありません

# 特記事項

- 翻訳の際に`詳細な`という文言は入れない
- 以下「プロンプト分類名」の場合「英語-日本語変換表の json ファイル」として作成しない
  - `Base Positive Prompt`
  - `Must Positive Prompt`
  - `Display`
  - `Setting`


# 関連ファイル, フォルダ

- `/ImageViewer/imageviewer/static/prompts`
- `/ImageViewer/imageviewer/static/translate_json`

---
以下のステップで進みたいですが、各ステップ毎に先へ進んでいいか確認してください

1. `/ImageViewer/imageviewer/static/prompts/illustration/rpg_icon/monster` フォルダ以下にあるプロンプトファイルについて作業をして

それではステップ1からお願いします
