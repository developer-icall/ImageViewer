# ImageViewer

## 概要
本プロジェクトは、Python + Flask で構築したAI画像販売、配布用の簡易Webシステムです。

## 機能
- 指定フォルダ(static/sync_images)以下にあるフォルダ内を検索し、1件目の画像サムネイル(sample-thumbnail内)を一覧表示します
- 画像サムネイルをクリックすると、対象人物の別ポーズ・衣装の画像一覧へ遷移します
- URLのパラメータに`hidden_secret_param_is_sample=False`を追加すると画像サムネイルから Sample の文字が消えます

## 使用方法
1. 下記 インストール手順 に従って諸々セットアップする
2. `poetry run python app.py` でファイルを実行する
3. ブラウザで http://192.168.1.130:5000/ へアクセスする

## インストール手順
1. Pythonをインストールする
    - Python 3.10.6 で動作確認済み
2. Python 仮想環境の作成
    1. カレントディレクトリにて以下を実行
        ```
        python -m venv venv
        ```
    2. 仮想環境を開始
        ```
        .\venv\Scripts\activate
        # 以下のように表示されていればOK
        (venv) PS C:\GitLab\laboratory\rpa\jinji-koka-rpa>
        ```
        - ※エラーが出るようであれば管理者権限で PowerShell を起動し、上記コマンドを実行することで解消される可能性があります
3. 仮想環境にて以下のコマンドでライブラリをインストールする
    ```
    # pip を最新版に更新
    python -m pip install --upgrade pip

    # 必要なモジュールをインストール
    pip install Flask
    ```
