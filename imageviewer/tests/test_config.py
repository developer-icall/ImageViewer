import os
import sys
import json

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
    get_first_visible_subcategory,
    has_visible_subcategories,
    get_style_by_id,
    get_category_by_id,
    get_subcategory_by_id
)

def test_load_config():
    """設定ファイルの読み込みをテストする関数"""
    config = load_config()
    print("設定ファイルの読み込み結果:")
    print(f"スタイル数: {len(config.get('styles', []))}")
    print(f"カテゴリ数: {len(config.get('categories', []))}")
    print(f"サブカテゴリ数: {len(config.get('subcategories', []))}")
    return config

def test_get_styles(config=None):
    """スタイル一覧の取得をテストする関数"""
    styles = get_styles(config)
    print("\nスタイル一覧:")
    for style in styles:
        print(f"ID: {style.get('id')}, 名前: {style.get('name')}, 表示順: {style.get('display_order')}, 表示: {style.get('visible')}")
    return styles

def test_get_categories(style_id, config=None):
    """カテゴリ一覧の取得をテストする関数"""
    categories = get_categories(style_id, config)
    print(f"\nスタイル '{style_id}' のカテゴリ一覧:")
    for category in categories:
        print(f"ID: {category.get('id')}, 名前: {category.get('name')}, 表示順: {category.get('display_order')}, 表示: {category.get('visible')}")
    return categories

def test_get_subcategories(style_id, category_id, config=None):
    """サブカテゴリ一覧の取得をテストする関数"""
    subcategories = get_subcategories(style_id, category_id, config)
    print(f"\nスタイル '{style_id}', カテゴリ '{category_id}' のサブカテゴリ一覧:")
    for subcategory in subcategories:
        print(f"ID: {subcategory.get('id')}, 名前: {subcategory.get('name')}, 表示順: {subcategory.get('display_order')}, 表示: {subcategory.get('visible')}")
    return subcategories

def test_get_first_visible_items(config=None):
    """最初の表示可能なアイテムの取得をテストする関数"""
    first_style = get_first_visible_style(config)
    print(f"\n最初の表示可能なスタイル: {first_style.get('id') if first_style else None}")

    if first_style:
        first_category = get_first_visible_category(first_style.get('id'), config)
        print(f"最初の表示可能なカテゴリ: {first_category.get('id') if first_category else None}")

        if first_category:
            first_subcategory = get_first_visible_subcategory(first_style.get('id'), first_category.get('id'), config)
            print(f"最初の表示可能なサブカテゴリ: {first_subcategory.get('id') if first_subcategory else None}")

            has_subcategories = has_visible_subcategories(first_style.get('id'), first_category.get('id'), config)
            print(f"サブカテゴリが存在するか: {has_subcategories}")

def test_get_items_by_id(config=None):
    """IDによるアイテムの取得をテストする関数"""
    style = get_style_by_id("realistic", config)
    print(f"\nID 'realistic' のスタイル: {style.get('name') if style else None}")

    category = get_category_by_id("female", config)
    print(f"ID 'female' のカテゴリ: {category.get('name') if category else None}")

    subcategory = get_subcategory_by_id("normal", config)
    print(f"ID 'normal' のサブカテゴリ: {subcategory.get('name') if subcategory else None}")

def main():
    """メイン関数"""
    print("設定ファイルのテストを開始します...")

    # 設定ファイルの読み込み
    config = test_load_config()

    # スタイル一覧の取得
    styles = test_get_styles(config)

    # 各スタイルに対するカテゴリ一覧の取得
    for style in styles:
        style_id = style.get('id')
        categories = test_get_categories(style_id, config)

        # 各カテゴリに対するサブカテゴリ一覧の取得
        for category in categories:
            category_id = category.get('id')
            test_get_subcategories(style_id, category_id, config)

    # 最初の表示可能なアイテムの取得
    test_get_first_visible_items(config)

    # IDによるアイテムの取得
    test_get_items_by_id(config)

    print("\nテストが完了しました。")

if __name__ == "__main__":
    main()