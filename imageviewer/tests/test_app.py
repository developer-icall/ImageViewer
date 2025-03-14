import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# テスト対象のモジュールのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestApp(unittest.TestCase):
    """app.pyの機能をテストするクラス"""

    def setUp(self):
        """テスト用のクライアントを準備"""
        app.config['TESTING'] = True
        self.client = app.test_client()

        # テスト用の設定データ
        self.test_config = {
            "styles": [
                {
                    "id": "realistic",
                    "name": "リアルテイスト画像",
                    "display_order": 1,
                    "visible": True
                },
                {
                    "id": "illustration",
                    "name": "ゲーム、イラスト風画像",
                    "display_order": 2,
                    "visible": True
                }
            ],
            "categories": [
                {
                    "id": "female",
                    "name": "女性",
                    "display_order": 1,
                    "visible": True,
                    "styles": ["realistic", "illustration"]
                },
                {
                    "id": "male",
                    "name": "男性",
                    "display_order": 2,
                    "visible": True,
                    "styles": ["realistic", "illustration"]
                }
            ],
            "subcategories": [
                {
                    "id": "normal",
                    "name": "通常画像",
                    "display_order": 1,
                    "visible": True,
                    "categories": ["female", "male"],
                    "styles": ["realistic", "illustration"]
                },
                {
                    "id": "transparent",
                    "name": "透明背景画像",
                    "display_order": 2,
                    "visible": True,
                    "categories": ["female", "male"],
                    "styles": ["realistic", "illustration"]
                }
            ]
        }

    @patch('app.load_config')
    @patch('app.get_first_visible_style')
    @patch('app.get_first_visible_category')
    @patch('app.get_first_visible_subcategory')
    def test_index_redirect(self, mock_get_first_visible_subcategory, mock_get_first_visible_category, mock_get_first_visible_style, mock_load_config):
        """ルートURLへのアクセスが正しくリダイレクトされるかテスト"""
        # モックの設定
        mock_load_config.return_value = self.test_config
        mock_get_first_visible_style.return_value = {"id": "realistic", "name": "リアルテイスト画像"}
        mock_get_first_visible_category.return_value = {"id": "female", "name": "女性"}
        mock_get_first_visible_subcategory.return_value = {"id": "normal", "name": "通常画像"}

        # リクエストの実行
        response = self.client.get('/')

        # 結果の検証
        self.assertEqual(response.status_code, 302)  # リダイレクトのステータスコード
        self.assertEqual(response.location, '/image_pattern/realistic/female/normal/')

    @patch('app.load_config')
    @patch('app.get_first_visible_style')
    @patch('app.get_first_visible_category')
    @patch('app.get_first_visible_subcategory')
    def test_image_pattern_root_redirect(self, mock_get_first_visible_subcategory, mock_get_first_visible_category, mock_get_first_visible_style, mock_load_config):
        """image_pattern/へのアクセスが正しくリダイレクトされるかテスト"""
        # モックの設定
        mock_load_config.return_value = self.test_config
        mock_get_first_visible_style.return_value = {"id": "realistic", "name": "リアルテイスト画像"}
        mock_get_first_visible_category.return_value = {"id": "female", "name": "女性"}
        mock_get_first_visible_subcategory.return_value = {"id": "normal", "name": "通常画像"}

        # リクエストの実行
        response = self.client.get('/image_pattern/')

        # 結果の検証
        self.assertEqual(response.status_code, 302)  # リダイレクトのステータスコード
        self.assertEqual(response.location, '/image_pattern/realistic/female/normal/')

    @patch('app.load_config')
    @patch('app.get_style_by_id')
    @patch('app.get_first_visible_style')
    def test_invalid_style_redirect(self, mock_get_first_visible_style, mock_get_style_by_id, mock_load_config):
        """存在しないスタイルへのアクセスが正しくリダイレクトされるかテスト"""
        # モックの設定
        mock_load_config.return_value = self.test_config
        mock_get_style_by_id.return_value = None  # スタイルが存在しない
        mock_get_first_visible_style.return_value = {"id": "realistic", "name": "リアルテイスト画像"}

        # リクエストの実行
        response = self.client.get('/image_pattern/non_existent/female/normal/')

        # 結果の検証
        self.assertEqual(response.status_code, 302)  # リダイレクトのステータスコード
        self.assertTrue('/image_pattern/realistic/' in response.location)

    @patch('app.load_config')
    @patch('app.get_style_by_id')
    @patch('app.get_category_by_id')
    @patch('app.get_categories')
    @patch('app.get_first_visible_category')
    def test_invalid_category_redirect(self, mock_get_first_visible_category, mock_get_categories, mock_get_category_by_id, mock_get_style_by_id, mock_load_config):
        """存在しないカテゴリへのアクセスが正しくリダイレクトされるかテスト"""
        # モックの設定
        mock_load_config.return_value = self.test_config
        mock_get_style_by_id.return_value = {"id": "realistic", "name": "リアルテイスト画像"}
        mock_get_category_by_id.return_value = None  # カテゴリが存在しない
        mock_get_categories.return_value = [{"id": "female", "name": "女性"}]
        mock_get_first_visible_category.return_value = {"id": "female", "name": "女性"}

        # リクエストの実行
        response = self.client.get('/image_pattern/realistic/non_existent/normal/')

        # 結果の検証
        self.assertEqual(response.status_code, 302)  # リダイレクトのステータスコード
        self.assertTrue('/image_pattern/realistic/female/' in response.location)

    @patch('app.load_config')
    @patch('app.get_style_by_id')
    @patch('app.get_category_by_id')
    @patch('app.get_categories')
    @patch('app.get_subcategories')
    @patch('app.get_first_visible_subcategory')
    def test_invalid_subcategory_redirect(self, mock_get_first_visible_subcategory, mock_get_subcategories, mock_get_categories, mock_get_category_by_id, mock_get_style_by_id, mock_load_config):
        """存在しないサブカテゴリへのアクセスが正しくリダイレクトされるかテスト"""
        # モックの設定
        mock_load_config.return_value = self.test_config
        mock_get_style_by_id.return_value = {"id": "realistic", "name": "リアルテイスト画像"}
        mock_get_category_by_id.return_value = {"id": "female", "name": "女性"}
        mock_get_categories.return_value = [{"id": "female", "name": "女性"}]
        mock_get_subcategories.return_value = [{"id": "normal", "name": "通常画像"}]
        mock_get_first_visible_subcategory.return_value = {"id": "normal", "name": "通常画像"}

        # リクエストの実行
        response = self.client.get('/image_pattern/realistic/female/non_existent/')

        # 結果の検証
        self.assertEqual(response.status_code, 302)  # リダイレクトのステータスコード
        self.assertTrue('/image_pattern/realistic/female/normal/' in response.location)

    @patch('app.load_config')
    @patch('app.get_style_by_id')
    @patch('app.get_category_by_id')
    @patch('app.get_categories')
    @patch('app.get_first_visible_subcategory')
    def test_category_without_subcategory_redirect(self, mock_get_first_visible_subcategory, mock_get_categories, mock_get_category_by_id, mock_get_style_by_id, mock_load_config):
        """サブカテゴリが指定されていない場合のリダイレクトをテスト"""
        # モックの設定
        mock_load_config.return_value = self.test_config
        mock_get_style_by_id.return_value = {"id": "realistic", "name": "リアルテイスト画像"}
        mock_get_category_by_id.return_value = {"id": "female", "name": "女性"}
        mock_get_categories.return_value = [{"id": "female", "name": "女性"}]
        mock_get_first_visible_subcategory.return_value = {"id": "normal", "name": "通常画像"}

        # リクエストの実行
        response = self.client.get('/image_pattern/realistic/female/')

        # 結果の検証
        self.assertEqual(response.status_code, 302)  # リダイレクトのステータスコード
        self.assertEqual(response.location, '/image_pattern/realistic/female/normal/')

if __name__ == '__main__':
    unittest.main()