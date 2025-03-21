仕様追加があるので実装お願いします

# 今回追加する仕様

1. 特定のモデルを使用して生成された画像の場合、クレジット表記をする
2. クレジット表記をする対象モデルを設定するファイルを作成し、それを参照する
3. モデルの情報は各画像ファイルと同階層、同名の JSON ファイルに記載されているものを参照する
  - 対象の JSON ファイルは app.py の 393 行目付近で読み込み、 create_prompt 関数内で使用しているものを使用する
4. 現状モデルのクレジット表記を行うのは `landscapeRealistic_v20WarmColor` のみ

# 特記事項

- 翻訳の際に`詳細な`という文言は入れない
- 以下「プロンプト分類名」の場合「英語-日本語変換表の json ファイル」として作成しない
  - `Base Positive Prompt`
  - `Base Positive Prompt`
  - `Must Positive Prompt`
  - `Display`
  - `Setting`


# 関連ファイル, フォルダ

- モデルの情報が記載されているファイル
  - `/ImageViewer/imageviewer/static/sync_images/<style>/<category>/<subcategory>/YYYYMMDD-HH-seed/XXXXX.json`
- 設定ファイルを配置するフォルダ
  - `/ImageViewer/imageviewer/config`
- クレジット表記を行う対象画面のテンプレートファイル
  - `/ImageViewer/imageviewer/templates/subfolders.html`
- メイン処理ファイル
  - `/ImageViewer/imageviewer/app.py`

---
以下のステップで進みたいですが、各ステップ毎に先へ進んでいいか確認してください

1. クレジット表記する対象モデルを設定するファイルを作成
2. 設定に従って必要に応じてクレジット表記を追加する

それではステップ1からお願いします
