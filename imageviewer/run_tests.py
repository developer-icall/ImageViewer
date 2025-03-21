import unittest
import os
import sys

# テストディレクトリのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tests')))

# テストを実行する関数
def run_tests():
    """すべてのテストを実行する関数"""
    # テストディレクトリ内のすべてのテストファイルを検索
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')

    # テストを実行
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # 結果を返す
    return result.wasSuccessful()

if __name__ == '__main__':
    # テストを実行
    success = run_tests()

    # 終了コードを設定
    sys.exit(0 if success else 1)