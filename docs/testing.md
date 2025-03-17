# ImageViewer テスト実施方法

このドキュメントでは、ImageViewerアプリケーションのテスト実施方法について説明します。

## テスト環境の準備

### 方法1: 仮想環境を使用する場合

1. 仮想環境を有効化します
   ```bash
   # Windows
   .\.venv\Scripts\activate

   # macOS/Linux
   source .venv/bin/activate
   ```

2. 必要なパッケージがインストールされていることを確認します
   ```bash
   # Poetryを使用してインストール
   poetry install
   ```

### 方法2: Poetryを直接使用する場合

1. Poetryがインストールされていることを確認します
   ```bash
   # Poetryのバージョン確認
   poetry --version
   ```

   インストールされていない場合は、[Poetry公式サイト](https://python-poetry.org/docs/#installation)の手順に従ってインストールしてください。

2. 依存パッケージをインストールします
   ```bash
   # プロジェクトルートディレクトリで実行
   poetry install
   ```

3. Poetry環境を有効化します
   ```bash
   # Poetry仮想環境をアクティベート
   poetry shell
   ```

## テストの実行方法

### 1. 全テストの実行

仮想環境内またはPoetry環境内でプロジェクトルートディレクトリから以下のコマンドを実行します：

```bash
cd imageviewer
python run_tests.py
```

または、環境を有効化せずに直接実行する場合：

```bash
poetry run python imageviewer/run_tests.py
```

このコマンドは、`tests`ディレクトリ内のすべてのテストファイルを実行します。

### 2. 特定のテストファイルの実行

特定のテストファイルのみを実行する場合は、以下のコマンドを使用します：

```bash
# 仮想環境内で
cd imageviewer
python -m unittest tests/test_config_utils.py

# または
poetry run python -m unittest imageviewer/tests/test_config_utils.py
```

### 3. 特定のテストケースやメソッドの実行

特定のテストケースやメソッドのみを実行する場合は、以下のコマンドを使用します：

```bash
# 仮想環境内で
cd imageviewer
python -m unittest tests.test_config_utils.TestConfigUtils.test_get_styles

# または
poetry run python -m unittest imageviewer.tests.test_config_utils.TestConfigUtils.test_get_styles
```

## テストの種類

### 1. ユニットテスト

`tests`ディレクトリには以下のユニットテストが含まれています：

- `test_config_utils.py`: 設定ファイル関連の機能をテスト
- `test_app.py`: アプリケーションのルーティングとリダイレクトをテスト

### 2. 手動テスト

以下の機能は手動でテストすることをお勧めします：

1. 画像表示機能
   - 各カテゴリの画像が正しく表示されるか
   - サムネイルがクリックできるか
   - 詳細ページに正しく遷移するか

2. 画像フィルタリング機能
   - 大項目（画像テイスト）の選択が正しく機能するか
   - 中項目（カテゴリ）の選択が正しく機能するか
   - 小項目（画像タイプ）の選択が正しく機能するか
   - 非表示設定が正しく反映されるか

3. ページネーション機能
   - ページ切り替えが正しく機能するか
   - 表示件数が正しいか

## テスト設定ファイルの変更方法

テスト用の設定ファイルを変更する場合は、`tests/test_config_utils.py`の`setUp`メソッド内の`test_config`変数を編集してください。

## インポートエラーの解決方法

テスト実行時にインポートエラーが発生した場合は、以下の方法で解決できます：

1. 直接ファイルパスを指定する方法
   ```python
   import os
   import sys

   # 直接ファイルパスを指定
   config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
   sys.path.insert(0, config_dir)
   from config_utils import ...
   ```

2. 相対インポートを使用する方法
   ```python
   from .config.config_utils import ...
   ```

3. 絶対パスを使用する方法
   ```python
   import os
   import sys

   current_dir = os.path.dirname(os.path.abspath(__file__))
   sys.path.insert(0, os.path.dirname(current_dir))
   from imageviewer.config.config_utils import ...
   ```

4. Poetryのパッケージ構造を活用する方法
   ```python
   # pyproject.tomlでパッケージが正しく設定されていれば
   from imageviewer.config.config_utils import ...
   ```

## テスト結果の確認

テスト実行後、コンソールに表示される結果を確認してください。すべてのテストが成功した場合は、以下のような出力が表示されます：

```
Ran X tests in Y.ZZZs

OK
```

テストが失敗した場合は、エラーメッセージを確認して問題を修正してください。