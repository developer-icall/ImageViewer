import os
import sys
import json
import unittest
from unittest.mock import patch, mock_open

# 絶対パスを使用してインポート
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(current_dir))
from config.config_utils import (
    load_config, get_styles, get_categories, get_subcategories,
    get_first_visible_style, get_first_visible_category, get_first_visible_subcategory,
    has_visible_subcategories, get_style_by_id, get_category_by_id, get_subcategory_by_id,
    are_all_subcategories_hidden, is_subcategory_visible_for_style_category
)

class TestConfigUtils(unittest.TestCase):
    """config_utils.pyの機能をテストするクラス"""

    def setUp(self):
        """テスト用の設定データを準備"""
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
                },
                {
                    "id": "hidden_style",
                    "name": "非表示スタイル",
                    "display_order": 3,
                    "visible": False
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
                },
                {
                    "id": "hidden_category",
                    "name": "非表示カテゴリ",
                    "display_order": 3,
                    "visible": False,
                    "styles": ["realistic", "illustration"]
                },
                {
                    "id": "all_hidden_subcategories",
                    "name": "すべてのサブカテゴリが非表示",
                    "display_order": 4,
                    "visible": True,
                    "styles": ["realistic", "illustration"]
                },
                {
                    "id": "no_subcategories",
                    "name": "サブカテゴリなし",
                    "display_order": 5,
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
                    "styles": ["realistic", "illustration"],
                    "excluded_combinations": [
                        {
                            "style": "illustration",
                            "category": "male"
                        }
                    ]
                },
                {
                    "id": "selfie",
                    "name": "セルフィー画像",
                    "display_order": 3,
                    "visible": True,
                    "categories": ["female", "male"],
                    "styles": ["realistic", "illustration"],
                    "excluded_combinations": [
                        {
                            "style": "realistic",
                            "category": "male"
                        }
                    ]
                },
                {
                    "id": "hidden_subcategory",
                    "name": "非表示サブカテゴリ",
                    "display_order": 3,
                    "visible": False,
                    "categories": ["female", "male"],
                    "styles": ["realistic", "illustration"]
                },
                {
                    "id": "hidden_subcategory1",
                    "name": "非表示サブカテゴリ1",
                    "display_order": 1,
                    "visible": False,
                    "categories": ["all_hidden_subcategories"],
                    "styles": ["realistic", "illustration"]
                },
                {
                    "id": "hidden_subcategory2",
                    "name": "非表示サブカテゴリ2",
                    "display_order": 2,
                    "visible": False,
                    "categories": ["all_hidden_subcategories"],
                    "styles": ["realistic", "illustration"]
                }
            ]
        }

    @patch('config.config_utils.open', new_callable=mock_open)
    @patch('config.config_utils.json.load')
    def test_load_config(self, mock_json_load, mock_file_open):
        """load_config関数のテスト"""
        # モックの設定
        mock_json_load.return_value = self.test_config

        # 関数の実行
        result = load_config()

        # 結果の検証
        self.assertEqual(result, self.test_config)
        mock_file_open.assert_called_once()
        mock_json_load.assert_called_once()

    def test_get_styles(self):
        """get_styles関数のテスト"""
        # 関数の実行
        result = get_styles(self.test_config)

        # 結果の検証
        self.assertEqual(len(result), 2)  # 表示可能なスタイルは2つ
        self.assertEqual(result[0]["id"], "realistic")  # 表示順が1番目
        self.assertEqual(result[1]["id"], "illustration")  # 表示順が2番目

    def test_get_categories(self):
        """get_categories関数のテスト"""
        # 関数の実行
        result = get_categories("realistic", self.test_config)

        # 結果の検証
        self.assertEqual(len(result), 4)  # 表示可能なカテゴリは4つ
        self.assertEqual(result[0]["id"], "female")  # 表示順が1番目
        self.assertEqual(result[1]["id"], "male")  # 表示順が2番目
        self.assertEqual(result[2]["id"], "all_hidden_subcategories")  # 表示順が3番目
        self.assertEqual(result[3]["id"], "no_subcategories")  # 表示順が4番目

    def test_is_subcategory_visible_for_style_category(self):
        """is_subcategory_visible_for_style_category関数のテスト"""
        # 通常のサブカテゴリ（すべての組み合わせで表示可能）
        normal = next(s for s in self.test_config["subcategories"] if s["id"] == "normal")
        self.assertTrue(is_subcategory_visible_for_style_category(normal, "realistic", "female"))
        self.assertTrue(is_subcategory_visible_for_style_category(normal, "realistic", "male"))
        self.assertTrue(is_subcategory_visible_for_style_category(normal, "illustration", "female"))
        self.assertTrue(is_subcategory_visible_for_style_category(normal, "illustration", "male"))

        # 特定の組み合わせが除外されているサブカテゴリ
        transparent = next(s for s in self.test_config["subcategories"] if s["id"] == "transparent")
        self.assertTrue(is_subcategory_visible_for_style_category(transparent, "realistic", "female"))
        self.assertTrue(is_subcategory_visible_for_style_category(transparent, "realistic", "male"))
        self.assertTrue(is_subcategory_visible_for_style_category(transparent, "illustration", "female"))
        self.assertFalse(is_subcategory_visible_for_style_category(transparent, "illustration", "male"))

        selfie = next(s for s in self.test_config["subcategories"] if s["id"] == "selfie")
        self.assertTrue(is_subcategory_visible_for_style_category(selfie, "realistic", "female"))
        self.assertFalse(is_subcategory_visible_for_style_category(selfie, "realistic", "male"))
        self.assertTrue(is_subcategory_visible_for_style_category(selfie, "illustration", "female"))
        self.assertTrue(is_subcategory_visible_for_style_category(selfie, "illustration", "male"))

        # 非表示のサブカテゴリ
        hidden = next(s for s in self.test_config["subcategories"] if s["id"] == "hidden_subcategory")
        self.assertFalse(is_subcategory_visible_for_style_category(hidden, "realistic", "female"))
        self.assertFalse(is_subcategory_visible_for_style_category(hidden, "realistic", "male"))
        self.assertFalse(is_subcategory_visible_for_style_category(hidden, "illustration", "female"))
        self.assertFalse(is_subcategory_visible_for_style_category(hidden, "illustration", "male"))

    def test_get_subcategories(self):
        """get_subcategories関数のテスト"""
        # realistic + female の組み合わせ
        result = get_subcategories("realistic", "female", self.test_config)
        self.assertEqual(len(result), 3)  # 表示可能なサブカテゴリは3つ
        self.assertEqual(result[0]["id"], "normal")
        self.assertEqual(result[1]["id"], "transparent")
        self.assertEqual(result[2]["id"], "selfie")

        # realistic + male の組み合わせ
        result = get_subcategories("realistic", "male", self.test_config)
        self.assertEqual(len(result), 2)  # 表示可能なサブカテゴリは2つ
        self.assertEqual(result[0]["id"], "normal")
        self.assertEqual(result[1]["id"], "transparent")
        # selfieは除外されている

        # illustration + female の組み合わせ
        result = get_subcategories("illustration", "female", self.test_config)
        self.assertEqual(len(result), 3)  # 表示可能なサブカテゴリは3つ
        self.assertEqual(result[0]["id"], "normal")
        self.assertEqual(result[1]["id"], "transparent")
        self.assertEqual(result[2]["id"], "selfie")

        # illustration + male の組み合わせ
        result = get_subcategories("illustration", "male", self.test_config)
        self.assertEqual(len(result), 2)  # 表示可能なサブカテゴリは2つ
        self.assertEqual(result[0]["id"], "normal")
        self.assertEqual(result[1]["id"], "selfie")
        # transparentは除外されている

    def test_get_first_visible_style(self):
        """get_first_visible_style関数のテスト"""
        # 関数の実行
        result = get_first_visible_style(self.test_config)

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "realistic")  # 表示順が1番目のスタイル

    def test_get_first_visible_category(self):
        """get_first_visible_category関数のテスト"""
        # 関数の実行
        result = get_first_visible_category("realistic", self.test_config)

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "female")  # 表示順が1番目のカテゴリ

    def test_get_first_visible_subcategory(self):
        """get_first_visible_subcategory関数のテスト"""
        # realistic + female の組み合わせ
        result = get_first_visible_subcategory("realistic", "female", self.test_config)
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "normal")  # 表示順が1番目のサブカテゴリ

        # illustration + male の組み合わせ
        result = get_first_visible_subcategory("illustration", "male", self.test_config)
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "normal")  # 表示順が1番目のサブカテゴリ

    def test_has_visible_subcategories(self):
        """has_visible_subcategories関数のテスト"""
        # 表示可能なサブカテゴリがある場合
        result = has_visible_subcategories("realistic", "female", self.test_config)
        self.assertTrue(result)

        # 表示可能なサブカテゴリがある場合（一部除外あり）
        result = has_visible_subcategories("realistic", "male", self.test_config)
        self.assertTrue(result)

        # すべてのサブカテゴリが非表示の場合
        result = has_visible_subcategories("realistic", "all_hidden_subcategories", self.test_config)
        self.assertFalse(result)

    def test_are_all_subcategories_hidden(self):
        """are_all_subcategories_hidden関数のテスト"""
        # 表示可能なサブカテゴリがある場合
        result = are_all_subcategories_hidden("realistic", "female", self.test_config)
        self.assertFalse(result)  # すべてのサブカテゴリが非表示ではない

        # 表示可能なサブカテゴリがある場合（一部除外あり）
        result = are_all_subcategories_hidden("realistic", "male", self.test_config)
        self.assertFalse(result)  # すべてのサブカテゴリが非表示ではない

        # すべてのサブカテゴリが非表示の場合
        result = are_all_subcategories_hidden("realistic", "all_hidden_subcategories", self.test_config)
        self.assertTrue(result)  # すべてのサブカテゴリが非表示

        # サブカテゴリがない場合
        result = are_all_subcategories_hidden("realistic", "no_subcategories", self.test_config)
        self.assertTrue(result)  # サブカテゴリがないのですべて非表示と見なす

    def test_get_style_by_id(self):
        """get_style_by_id関数のテスト"""
        # 関数の実行
        result = get_style_by_id("realistic", self.test_config)

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "realistic")

        # 存在しないIDの場合
        result = get_style_by_id("non_existent", self.test_config)
        self.assertIsNone(result)

        # 非表示のIDの場合
        result = get_style_by_id("hidden_style", self.test_config)
        self.assertIsNone(result)

    def test_get_category_by_id(self):
        """get_category_by_id関数のテスト"""
        # 関数の実行
        result = get_category_by_id("female", self.test_config)

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "female")

        # 存在しないIDの場合
        result = get_category_by_id("non_existent", self.test_config)
        self.assertIsNone(result)

        # 非表示のIDの場合
        result = get_category_by_id("hidden_category", self.test_config)
        self.assertIsNone(result)

    def test_get_subcategory_by_id(self):
        """get_subcategory_by_id関数のテスト"""
        # 関数の実行
        result = get_subcategory_by_id("normal", self.test_config)

        # 結果の検証
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "normal")

        # 存在しないIDの場合
        result = get_subcategory_by_id("non_existent", self.test_config)
        self.assertIsNone(result)

        # 非表示のIDの場合
        result = get_subcategory_by_id("hidden_subcategory", self.test_config)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()