import os
import json
from typing import Dict, List, Any, Optional

# 設定ファイルのパス
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'image_pattern_config.json')

def load_config() -> Dict[str, Any]:
    """
    設定ファイルを読み込む関数

    Returns:
        Dict[str, Any]: 設定情報を含む辞書
    """
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"設定ファイルの読み込みに失敗しました: {e}")
        # デフォルト設定を返す
        return {
            "styles": [],
            "categories": [],
            "subcategories": []
        }

def get_styles(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    スタイル（大項目）の一覧を取得する関数

    Args:
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        List[Dict[str, Any]]: スタイル情報のリスト（表示順でソート済み）
    """
    if config is None:
        config = load_config()

    # 表示順でソート
    return sorted([style for style in config.get("styles", []) if style.get("visible", True)],
                 key=lambda x: x.get("display_order", 999))

def get_categories(style_id: str, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    指定されたスタイルに対応するカテゴリ（中項目）の一覧を取得する関数

    Args:
        style_id (str): スタイルID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        List[Dict[str, Any]]: カテゴリ情報のリスト（表示順でソート済み）
    """
    if config is None:
        config = load_config()

    # 指定されたスタイルに対応するカテゴリを抽出し、表示順でソート
    return sorted([category for category in config.get("categories", [])
                  if style_id in category.get("styles", []) and category.get("visible", True)],
                 key=lambda x: x.get("display_order", 999))

def is_subcategory_visible_for_style_category(subcategory: Dict[str, Any], style_id: str, category_id: str) -> bool:
    """
    サブカテゴリが指定されたスタイルとカテゴリの組み合わせで表示可能かどうかを確認する関数

    Args:
        subcategory (Dict[str, Any]): サブカテゴリ情報
        style_id (str): スタイルID
        category_id (str): カテゴリID

    Returns:
        bool: 表示可能な場合はTrue、そうでない場合はFalse
    """
    # サブカテゴリ自体が非表示の場合はFalse
    if not subcategory.get("visible", True):
        return False

    # スタイルとカテゴリの両方が含まれているか確認
    if style_id not in subcategory.get("styles", []) or category_id not in subcategory.get("categories", []):
        return False

    # 特定のスタイルとカテゴリの組み合わせに対する非表示設定があるか確認
    excluded_combinations = subcategory.get("excluded_combinations", [])
    for combo in excluded_combinations:
        if combo.get("style") == style_id and combo.get("category") == category_id:
            return False

    return True

def get_subcategories(style_id: str, category_id: str, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    指定されたスタイルとカテゴリに対応するサブカテゴリ（小項目）の一覧を取得する関数

    Args:
        style_id (str): スタイルID
        category_id (str): カテゴリID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        List[Dict[str, Any]]: サブカテゴリ情報のリスト（表示順でソート済み）
    """
    if config is None:
        config = load_config()

    # 指定されたスタイルとカテゴリに対応するサブカテゴリを抽出し、表示順でソート
    return sorted([subcategory for subcategory in config.get("subcategories", [])
                  if is_subcategory_visible_for_style_category(subcategory, style_id, category_id)],
                 key=lambda x: x.get("display_order", 999))

def get_first_visible_style(config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    表示順が最初の表示可能なスタイルを取得する関数

    Args:
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        Optional[Dict[str, Any]]: スタイル情報。見つからない場合はNone。
    """
    styles = get_styles(config)
    return styles[0] if styles else None

def get_first_visible_category(style_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    指定されたスタイルに対応する表示順が最初の表示可能なカテゴリを取得する関数

    Args:
        style_id (str): スタイルID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        Optional[Dict[str, Any]]: カテゴリ情報。見つからない場合はNone。
    """
    categories = get_categories(style_id, config)
    return categories[0] if categories else None

def get_first_visible_subcategory(style_id: str, category_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    指定されたスタイルとカテゴリに対応する表示順が最初の表示可能なサブカテゴリを取得する関数

    Args:
        style_id (str): スタイルID
        category_id (str): カテゴリID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        Optional[Dict[str, Any]]: サブカテゴリ情報。見つからない場合はNone。
    """
    subcategories = get_subcategories(style_id, category_id, config)
    return subcategories[0] if subcategories else None

def has_visible_subcategories(style_id: str, category_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """
    指定されたスタイルとカテゴリに対応する表示可能なサブカテゴリが存在するかを確認する関数

    Args:
        style_id (str): スタイルID
        category_id (str): カテゴリID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        bool: 表示可能なサブカテゴリが存在する場合はTrue、そうでない場合はFalse
    """
    # 表示可能なサブカテゴリの数を確認
    visible_subcategories = get_subcategories(style_id, category_id, config)
    return len(visible_subcategories) > 0

def get_all_subcategories_for_category(category_id: str, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    指定されたカテゴリに対応するすべてのサブカテゴリ（表示/非表示問わず）を取得する関数

    Args:
        category_id (str): カテゴリID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        List[Dict[str, Any]]: サブカテゴリ情報のリスト
    """
    if config is None:
        config = load_config()

    # 指定されたカテゴリに対応するすべてのサブカテゴリを抽出
    return [subcategory for subcategory in config.get("subcategories", [])
            if category_id in subcategory.get("categories", [])]

def are_all_subcategories_hidden(style_id: str, category_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """
    指定されたスタイルとカテゴリに対応するすべてのサブカテゴリが非表示かどうかを確認する関数

    Args:
        style_id (str): スタイルID
        category_id (str): カテゴリID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        bool: すべてのサブカテゴリが非表示の場合はTrue、表示可能なサブカテゴリが1つでもある場合はFalse
    """
    if config is None:
        config = load_config()

    # カテゴリに対応するすべてのサブカテゴリを取得
    all_subcategories = [subcategory for subcategory in config.get("subcategories", [])
                         if style_id in subcategory.get("styles", []) and
                            category_id in subcategory.get("categories", [])]

    # サブカテゴリがない場合はTrueを返す（すべて非表示と見なす）
    if not all_subcategories:
        return True

    # すべてのサブカテゴリが指定されたスタイルとカテゴリの組み合わせで非表示かどうかを確認
    return all(not is_subcategory_visible_for_style_category(subcategory, style_id, category_id)
               for subcategory in all_subcategories)

def get_style_by_id(style_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    指定されたIDのスタイルを取得する関数

    Args:
        style_id (str): スタイルID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        Optional[Dict[str, Any]]: スタイル情報。見つからない場合はNone。
    """
    if config is None:
        config = load_config()

    for style in config.get("styles", []):
        if style.get("id") == style_id and style.get("visible", True):
            return style
    return None

def get_category_by_id(category_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    指定されたIDのカテゴリを取得する関数

    Args:
        category_id (str): カテゴリID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        Optional[Dict[str, Any]]: カテゴリ情報。見つからない場合はNone。
    """
    if config is None:
        config = load_config()

    for category in config.get("categories", []):
        if category.get("id") == category_id and category.get("visible", True):
            return category
    return None

def get_subcategory_by_id(subcategory_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    指定されたIDのサブカテゴリを取得する関数

    Args:
        subcategory_id (str): サブカテゴリID
        config (Optional[Dict[str, Any]], optional): 設定情報。Noneの場合は読み込む。

    Returns:
        Optional[Dict[str, Any]]: サブカテゴリ情報。見つからない場合はNone。
    """
    if config is None:
        config = load_config()

    for subcategory in config.get("subcategories", []):
        if subcategory.get("id") == subcategory_id and subcategory.get("visible", True):
            return subcategory
    return None