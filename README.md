# ImageViewer

## 概要
本プロジェクトは、Python + Flask で構築したAI画像販売、配布用の簡易Webシステムです。

## 機能
- 指定フォルダ(static/sync_images)以下にあるフォルダ内を検索し、1件目の画像サムネイル(sample-thumbnail内)を一覧表示します
- 画像サムネイルをクリックすると、対象人物の別ポーズ・衣装の画像一覧へ遷移します

## 各種ファイル
- アプリ設定・定数などがまとまった根幹となるファイル `imageviewer\app.py`
- テンプレート `imageviewer\templates`
- scss `imageviewer\static\css\customize.scss`
- UI用の画像 `imageviewer\static\ui_images`
  - ※AI生成した画像については別フォルダで管理します。詳しくは後述します

## 使用方法
1. 下記 インストール手順 に従って諸々セットアップする
2. `.\ImageViewer\imageviewer` ディレクトリにて `poetry run python app.py` でファイルを実行する
3. ブラウザで http://{ローカルIP}:5000/ へアクセスする
4. 【! gitには反映しないでください !】ホットリロード有効化のため、app.py末尾を以下のように書き換える
    ```
    if __name__ == '__main__':
        # デバッグモードを有効にし、ホットリロードを有効化
        app.run(debug=True, host='0.0.0.0', use_reloader=True)

    # 自動更新を有効にする設定を追加
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    ```

## インストール手順
1. Pythonをインストールする
    - Python 3.10.6 で動作確認済み
2. Poetry をインストールする
   ```
   python -m pip install --user poetry
   ```
   - 環境変数の PATH に poetry を追加
     - python のインストール環境に応じてPATH の設定が必要です
     - 例: `C:\Users\k.hongou\AppData\Roaming\Python\Python312\Scripts`
     - poetry への PATH が設定されていない場合は `C:\Users\k.hongou\AppData\Roaming\Python\Python312\Scripts\poetry run python app.py` などで動かすことも可能
3. Python 仮想環境の作成
    1. カレントディレクトリにて以下を実行
        ```
        python -m venv .venv
        ```
    2. 仮想環境を開始
        ```
        .\.venv\Scripts\activate
        # 以下のように表示されていればOK
        (venv) PS C:\Users\k.hongou\Documents\Codes\PythonProjects\ImageViewer>
        ```
        - ※エラーが出るようであれば管理者権限で PowerShell を起動し、上記コマンドを実行することで解消される可能性があります
4. 仮想環境にて以下のコマンドでライブラリをインストールする
    ```
    # pip を最新版に更新
    python -m pip install --upgrade pip

    # 必要なモジュールをインストール
    pip install Flask
    ```
5. imageviewer/static/sync_images フォルダを作成し、 AIで生成された画像フォルダを任意に配置してください
    - 女性、男性(-men)、セルフィー写真(-selfie)、透過写真(-transparent)、背景(-background)などの種類がフォルダ名で分かれています
    - 当該フォルダは、実際のサイト上ではシンボリックリンクとして扱われています
        - AutoImageGenerator で画像生成を行っている PC と ImageViewer が同じ PC の場合は、PowerShell(管理者で実行)にて以下のようなコマンド(環境によって変更)でシンボリックリンクを作成できます
            ```
            New-Item -ItemType SymbolicLink -Path "C:\Users\k.hongou\Documents\Codes\PythonProjects\ImageViewer\imageviewer\static\sync_images" -Target "C:\Users\k.hongou\Documents\Codes\PythonProjects\AutoImageGenerator\images\output"
            ```
