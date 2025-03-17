import os
import sys
import json
import unittest
from unittest.mock import patch, mock_open

# 現在のディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.config_utils import (
    load_config,
    get_styles,
    get_categories,
    get_subcategories,
    get_first_visible_style,
    get_first_visible_category,
    get_first_visible_subcategory
)

class TestDisplayOrder(unittest.TestCase):
    """表示順の制御機能をテストするクラス"""

    def setUp(self):
        """テスト用の設定データを準備"""
        self.test_config = {
            "styles": [
                {
                    "id": "style3",
                    "name": "スタイル3",
                    "display_order": 3,
                    "visible": True
                },
                {
                    "id": "style1",
                    "name": "スタイル1",
                    "display_order": 1,
                    "visible": True
                },
                {
                    "id": "style2",
                    "name": "スタイル2",
                    "display_order": 2,
                    "visible": True
                }
            ],
            "categories": [
                {
                    "id": "category3",
                    "name": "カテゴリ3",
                    "display_order": 3,
                    "visible": True,
                    "styles": ["style1", "style2", "style3"]
                },
                {
                    "id": "category1",
                    "name": "カテゴリ1",
                    "display_order": 1,
                    "visible": True,
                    "styles": ["style1", "style2", "style3"]
                },
                {
                    "id": "category2",
                    "name": "カテゴリ2",
                    "display_order": 2,
                    "visible": True,
                    "styles": ["style1", "style2", "style3"]
                }
            ],
            "subcategories": [
                {
                    "id": "subcategory3",
                    "name": "サブカテゴリ3",
                    "display_order": 3,
                    "visible": True,
                    "categories": ["category1", "category2", "category3"],
                    "styles": ["style1", "style2", "style3"]
                },
                {
                    "id": "subcategory1",
                    "name": "サブカテゴリ1",
                    "display_order": 1,
                    "visible": True,
                    "categories": ["category1", "category2", "category3"],
                    "styles": ["style1", "style2", "style3"]
                },
                {
                    "id": "subcategory2",
                    "name": "サブカテゴリ2",
                    "display_order": 2,
                    "visible": True,
                    "categories": ["category1", "category2", "category3"],
                    "styles": ["style1", "style2", "style3"]
                }
            ]
        }

    def test_styles_display_order(self):
        """スタイルの表示順をテスト"""
        # 関数の実行
        styles = get_styles(self.test_config)

        # 結果の検証
        self.assertEqual(len(styles), 3)
        self.assertEqual(styles[0]["id"], "style1")  # 表示順が1番目
        self.assertEqual(styles[1]["id"], "style2")  # 表示順が2番目
        self.assertEqual(styles[2]["id"], "style3")  # 表示順が3番目

    def test_categories_display_order(self):
        """カテゴリの表示順をテスト"""
        # 関数の実行
        categories = get_categories("style1", self.test_config)

        # 結果の検証
        self.assertEqual(len(categories), 3)
        self.assertEqual(categories[0]["id"], "category1")  # 表示順が1番目
        self.assertEqual(categories[1]["id"], "category2")  # 表示順が2番目
        self.assertEqual(categories[2]["id"], "category3")  # 表示順が3番目

    def test_subcategories_display_order(self):
        """サブカテゴリの表示順をテスト"""
        # 関数の実行
        subcategories = get_subcategories("style1", "category1", self.test_config)

        # 結果の検証
        self.assertEqual(len(subcategories), 3)
        self.assertEqual(subcategories[0]["id"], "subcategory1")  # 表示順が1番目
        self.assertEqual(subcategories[1]["id"], "subcategory2")  # 表示順が2番目
        self.assertEqual(subcategories[2]["id"], "subcategory3")  # 表示順が3番目

    def test_first_visible_style(self):
        """最初の表示可能なスタイルの取得をテスト"""
        # 関数の実行
        first_style = get_first_visible_style(self.test_config)

        # 結果の検証
        self.assertIsNotNone(first_style)
        self.assertEqual(first_style["id"], "style1")  # 表示順が1番目のスタイル

    def test_first_visible_category(self):
        """最初の表示可能なカテゴリの取得をテスト"""
        # 関数の実行
        first_category = get_first_visible_category("style1", self.test_config)

        # 結果の検証
        self.assertIsNotNone(first_category)
        self.assertEqual(first_category["id"], "category1")  # 表示順が1番目のカテゴリ

    def test_first_visible_subcategory(self):
        """最初の表示可能なサブカテゴリの取得をテスト"""
        # 関数の実行
        first_subcategory = get_first_visible_subcategory("style1", "category1", self.test_config)

        # 結果の検証
        self.assertIsNotNone(first_subcategory)
        self.assertEqual(first_subcategory["id"], "subcategory1")  # 表示順が1番目のサブカテゴリ

    def test_change_display_order(self):
        """表示順を変更した場合のテスト"""
        # 表示順を変更
        modified_config = self.test_config.copy()
        modified_config["styles"][0]["display_order"] = 4  # style3の表示順を4に変更
        modified_config["categories"][0]["display_order"] = 4  # category3の表示順を4に変更
        modified_config["subcategories"][0]["display_order"] = 4  # subcategory3の表示順を4に変更

        # 関数の実行
        styles = get_styles(modified_config)
        categories = get_categories("style1", modified_config)
        subcategories = get_subcategories("style1", "category1", modified_config)

        # 結果の検証
        self.assertEqual(styles[0]["id"], "style1")
        self.assertEqual(styles[1]["id"], "style2")
        self.assertEqual(styles[2]["id"], "style3")

        self.assertEqual(categories[0]["id"], "category1")
        self.assertEqual(categories[1]["id"], "category2")
        self.assertEqual(categories[2]["id"], "category3")

        self.assertEqual(subcategories[0]["id"], "subcategory1")
        self.assertEqual(subcategories[1]["id"], "subcategory2")
        self.assertEqual(subcategories[2]["id"], "subcategory3")

if __name__ == '__main__':
    unittest.main()