import os
import re
import json
import sys
from flask import Flask, render_template, send_from_directory, request, abort, g, redirect
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode

# 絶対パスを使用してインポート
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(current_dir))
from imageviewer.config.config_utils import (
    load_config, get_styles, get_categories, get_subcategories,
    get_first_visible_style, get_first_visible_category, get_first_visible_subcategory,
    has_visible_subcategories, are_all_subcategories_hidden, is_subcategory_visible_for_style_category,
    get_model_credit_info
)

app = Flask(__name__)

# ドメイン
DOMAIN_NAME = 'ai-gazou.com'

# 画像フォルダのパス
IMAGE_FOLDER = './static/sync_images'

# サムネイル用画像の保存先フォルダのパス
THUMBNAIL_FOLDER = "/thumbnail"

# 表示する画像をSample文字入りにするかのフラグ(True: Sample文字入り, False: Sample文字なし)
# 2025/1/21 一旦無料DL用ページとするため、Falseにする
SAMPLE_IMAGE_FLAG= False

# Sample文字が入っている等倍画像の保存先フォルダのパス
WITH_SAMPLE_TEXT_FOLDER = "/sample"

# Sample文字が入っていサムネイル用画像の保存先フォルダのパス
WITH_SAMPLE_THUMBNAIL_FOLDER = "/sample-thumbnail"

# 半分の解像度の画像保存先フォルダパス
HALF_RESOLUTION_FOLDER = "/half-resolution"

# 1ページ当たりの表示件数
INDEX_PER_PAGE = 12

# ページネーションに用いるgetパラメータの名前
PAGE_PARAMETER = 'page'

# 画像タイプを定義するクラスを追加
class ImageType:
    def __init__(self, is_sample=True, style=None, category=None, subcategory=None):
        self.is_sample = is_sample

        # 新しいフォルダ構造用のパラメータ
        self.style = style  # realistic または illustration
        self.category = category  # female, male, animal, background, rpg_icon, vehicle, other
        self.subcategory = subcategory  # normal, transparent, selfie, dog, cat, etc.

    def get_folder_path(self):
        # 新しいフォルダ構造
        base_path = os.path.join(IMAGE_FOLDER, self.style, self.category)

        # サブカテゴリが指定されている場合は追加
        if self.subcategory:
            return os.path.join(base_path, self.subcategory)
        return base_path

# テンプレートに渡す定数
@app.before_request
def before_request():
    g.domain_name = DOMAIN_NAME  # ドメイン
    g.site_name = DOMAIN_NAME  # サイト名
    g.prompt_separator = " / "  # プロンプトの区切り文字
    # 設定ファイルを読み込み、グローバル変数に設定
    g.config = load_config()
    # パラメータ群(上から順にURL末尾に付与する想定)
    g.url_parameter = get_url_parameter() # getパラメータ
    g.page_parameter = get_page_parameter() # pageパラメータ

# pageパラメータを除いたgetパラメータを取得
def get_parameters_excluding_page():
    parsed = urlparse(request.url)
    # pageパラメータを除外
    query_params = {k: v for k, v in parse_qs(parsed.query).items() if k != PAGE_PARAMETER}
    return query_params;

# 現在のgetパラメータ取得
def get_url_parameter():
    result = ''
    parameter = get_parameters_excluding_page()
    if parameter:  # page以外のパラメータが存在する場合そのまま返す
        result = '?' + urlencode(parameter, doseq=True)
    return result;

# pageパラメータを作成 ※=までの出力なので、ページ数はhtml側で別途書き足す
def get_page_parameter():
    head = '?'
    parameter = get_parameters_excluding_page()
    if parameter:  # page以外のパラメータが存在する場合頭文字を変更
        head = '&'
    return head + PAGE_PARAMETER + '='

# サーバーサイドでページネーション情報を計算
def get_pagination_info(total_items, items_per_page):
    page = request.args.get('page', type=int, default=1)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    return {
        'page': page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }

def get_first_image(subfolder_path):
    for root, dirs, files in os.walk(subfolder_path):
        files.sort()  # ファイル名順にソート
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_path = os.path.join(root, file).replace("\\", "/")

                # フォルダ名を取得（例：20231124-17-1409855962）
                folder_name = os.path.basename(os.path.dirname(os.path.dirname(image_path)))

                # 画像のURLパスを構築
                return f"/images/{folder_name}/thumbnail/{file}"
    return None

def get_subfolders(folder_path, page, image_type):
    # フォルダパスの決定
    folder_path = image_type.get_folder_path()

    # debug
    print(f"folder_path: {folder_path}")

    subfolders = []
    start_index = (page - 1) * INDEX_PER_PAGE
    end_index = start_index + INDEX_PER_PAGE
    print(f"start_index: {start_index}")
    print(f"end_index: {end_index}")
    index = 0
    total_count = 0

    # 全てのサブフォルダを収集
    all_valid_subfolders = []

    for root, dirs, files in os.walk(folder_path):
        dirs.sort()  # フォルダの一覧をABC順にソート
        for dir in dirs:
            subfolder_path = os.path.join(root, dir).replace("\\", "/")

            # サブフォルダの文字列にsample, sample-thumbnail, thumbnail, half_resolution が含まれた場合は除外
            if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER, WITH_SAMPLE_THUMBNAIL_FOLDER, THUMBNAIL_FOLDER, HALF_RESOLUTION_FOLDER]):
                continue

            # サムネイル画像の取得
            if image_type.is_sample:
                first_image = get_first_image(subfolder_path + WITH_SAMPLE_THUMBNAIL_FOLDER)
            else:
                if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER, WITH_SAMPLE_THUMBNAIL_FOLDER, THUMBNAIL_FOLDER]):
                    continue
                first_image = get_first_image(subfolder_path + THUMBNAIL_FOLDER)

            if first_image:
                all_valid_subfolders.append((dir, first_image))
            else:
                print(f"first image not found:{subfolder_path}")

    # 総数を記録
    total_count = len(all_valid_subfolders)

    # ページネーションに基づいて必要な部分だけを抽出
    if start_index < total_count:
        subfolders = all_valid_subfolders[start_index:min(end_index, total_count)]

    return subfolders, total_count

def extract_number(filename):
    match = re.match(r"(\d+)", filename)
    return int(match.group(1)) if match else float('inf')

# JSONファイルからモデル情報を取得する関数
def get_model_info_from_json(json_file_path: str) -> Optional[str]:
    """
    JSONファイルからモデル情報を取得する関数

    Args:
        json_file_path (str): JSONファイルのパス

    Returns:
        Optional[str]: モデル名。情報がない場合はNone
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            # モデル情報が含まれているかチェック
            if "sd_model" in data:
                return data["sd_model"]
    except Exception as e:
        print(f"JSONファイルの読み込みエラー: {e}")
    return None

# JSONを基に、プロンプト情報を生成
def create_prompt(json_file, properties):
    separator = g.prompt_separator
    data = json.load(json_file) # jsonファイルを読み込む
    result = []
    for property in properties:
        # プロパティが存在する場合のみ処理を行う
        if property in data:
            word = translate_prompt(property, separator.join(data[property]))
            if word:
                result.append(word)
    return separator.join(result)

# プロンプトを日本語に変換
def translate_prompt(json_name, prompt):
    # promptが空ならreturn
    if not prompt:
        return

    # まずすべて小文字に変換
    prompt_lower = prompt.lower()

    # 引数json_nameと同じ名を持つ翻訳対応表を呼び出す
    translate_words = ''

    # 引数json_nameと同じ名を持つ翻訳用JSONファイルの読み込み
    json_file_path = os.path.join('static', 'translate_json', f'{json_name}.json')
    # JSONがない場合はreturn
    if not os.path.isfile(json_file_path):
        return
    # JSONがある
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        translate_words = json.load(json_file)

    # 翻訳実行
    result = translate_text(prompt_lower, translate_words)

    # resultが空ならreturn
    if not result:
        return

    return result

# 翻訳処理
# text: 翻訳対象の文字列
# translation_dict: 翻訳対応表
def translate_text(text, translation_dict):
    translated_text = text

    # 翻訳対応表のキーと照合
    for target, translation_text in translation_dict.items():
        count = len(translation_text)
        # 翻訳対象が1文字以上なら
        if count > 0:
            # 対象を翻訳(日本語に置換)した上で前後に[]付与
            translated_text = translated_text.replace(target, "["+translation_text+"]")

    # []で囲まれた翻訳対象を抽出
    extracted_texts = [text.replace('[', '').replace(']', '').strip() for text in translated_text.split() if text.startswith('[') and text.endswith(']')]
    # 抽出結果を連結し文字列化
    concatenated_string = ''.join(extracted_texts)

    return concatenated_string

# 表示可能な画像一覧への誘導用HTMLを表示
def redirect_to_image_list(config, style=None, category=None):
    style_data = style
    if style is None:
        # 指定がないなら、取得可能な最初の値を使用
        first_style = get_first_visible_style(config)
        if first_style:
            style_data = first_style["id"]

    category_data = category
    if category is None:
        # 指定がないなら、取得可能な最初の値を使用
        first_category = get_first_visible_category(style_data, config)
        if first_category:
            category_data = first_category["id"]

    subcategory_data = None
    if style_data and category_data:
        # 最初の値を取得
        first_subcategory = get_first_visible_subcategory(style_data, category_data, config)
        if first_subcategory:
            # 選択された大項目および中項目に対する小項目がすべて非表示かどうかを確認
            all_subcategories_hidden = are_all_subcategories_hidden(style_data, category_data, config)
            if not all_subcategories_hidden:
                # 非表示でない場合は、最初の値を使用
                subcategory_data = first_subcategory["id"]

    # テンプレートに渡すデータを設定
    template_data = {
        # 設定ファイルから取得したデータを追加
        'style': style_data,
        'category': category_data,
        'subcategory': subcategory_data
    }
    # 表示可能な画像一覧への誘導用HTMLを表示
    return render_template('not_found.html', **template_data)

@app.route('/')
def index():
    # 設定ファイルから表示順が最初のスタイル、カテゴリ、サブカテゴリを取得
    config = g.config
    # 最初の表示可能なスタイル、カテゴリ、サブカテゴリにリダイレクト
    return redirect_to_image_list(config)

# 新しい汎用的なルート設定
@app.route('/image_pattern/<style>/<category>/')
@app.route('/image_pattern/<style>/<category>/<subcategory>/')
def image_pattern_route(style, category, subcategory=None):
    # 設定ファイルを取得
    config = g.config

    # スタイルが存在するか確認
    if not get_style_by_id(style, config):
        # 存在しない場合は最初の表示可能なスタイルにリダイレクト
        return redirect_to_image_list(config)

    # カテゴリが存在するか確認
    if not get_category_by_id(category, config) or category not in [c["id"] for c in get_categories(style, config)]:
        # 存在しない場合は指定されたスタイルの最初の表示可能なカテゴリにリダイレクト
        return redirect_to_image_list(config, style)

    # サブカテゴリが指定されていない場合
    if subcategory is None:
        # 指定されたスタイルとカテゴリの最初の表示可能なサブカテゴリにリダイレクト
        first_subcategory = get_first_visible_subcategory(style, category, config)
        if first_subcategory:
            return redirect_to_image_list(config, style, category)
        # サブカテゴリがない場合はそのまま表示
    else:
        # サブカテゴリが存在するか確認
        subcategories = get_subcategories(style, category, config)
        if not subcategories or subcategory not in [s["id"] for s in subcategories]:
            # 存在しない場合は指定されたスタイルとカテゴリの最初の表示可能なサブカテゴリにリダイレクト
            return redirect_to_image_list(config, style, category)
        else:
            # サブカテゴリが存在する場合でも、excluded_combinationsで非表示に設定されているか確認
            subcategory_obj = next((s for s in config.get("subcategories", []) if s.get("id") == subcategory), None)
            if subcategory_obj and not is_subcategory_visible_for_style_category(subcategory_obj, style, category):
                # 非表示の場合は最初の表示可能なサブカテゴリにリダイレクト
                return redirect_to_image_list(config, style, category)

    # 画像タイプの設定
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        style=style,
        category=category,
        subcategory=subcategory
    )

    # オプション取得
    options = [config.get("name") for config in [
        get_style_by_id(style, config),
        get_category_by_id(category, config),
        get_subcategory_by_id(subcategory, config)
    ] if config.get("id") != "normal"]  # normalを除外

    page = request.args.get('page', default=1, type=int)
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    # 選択された大項目および中項目に対する小項目がすべて非表示かどうかを確認
    all_subcategories_hidden = are_all_subcategories_hidden(style, category, config)

    # テンプレートに渡すデータを設定
    template_data = {
        'subfolder_images': subfolder_images,
        'pagination_info': pagination_info,
        'image_pattern_category': style,
        'image_pattern_subcategory': category,
        'image_pattern_type': subcategory,
        'options': options,
        # 設定ファイルから取得したデータを追加
        'styles': get_styles(config),
        'categories': get_categories(style, config),
        'subcategories': get_subcategories(style, category, config) if not all_subcategories_hidden else [],
        'has_subcategories': not all_subcategories_hidden
    }

    return render_template('index.html', **template_data)

# 新しい画像パターンのルーティング
@app.route('/image_pattern/')
def image_pattern_root():
    # 設定ファイルから表示順が最初のスタイル、カテゴリ、サブカテゴリを取得
    config = g.config
    # 最初の表示可能なスタイル、カテゴリ、サブカテゴリにリダイレクト
    return redirect_to_image_list(config)

# 新しい画像パターンのサブフォルダ表示用ルーティング
@app.route('/image_pattern/<style>/<category>/<subcategory>/subfolders/<subfolder_name>/', methods=['GET'])
def subfolders(style, category, subcategory, subfolder_name):
    # 設定ファイルを取得
    config = g.config

    # サブカテゴリが存在する場合でも、excluded_combinationsで非表示に設定されているか確認
    subcategory_obj = next((s for s in config.get("subcategories", []) if s.get("id") == subcategory), None)
    if subcategory_obj and not is_subcategory_visible_for_style_category(subcategory_obj, style, category):
        # 非表示の場合は最初の表示可能なサブカテゴリにリダイレクト
        return redirect_to_image_list(config, style, category)

    # 画像タイプの設定
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        style=style,
        category=category,
        subcategory=subcategory
    )

    # オプション取得
    options = [config.get("name") for config in [
        get_style_by_id(style, config),
        get_category_by_id(category, config),
        get_subcategory_by_id(subcategory, config)
    ] if config.get("id") != "normal"]  # normalを除外

    # ページネーションパラメータを取得（デフォルトは1ページ目）
    page = request.args.get('page', 1, type=int)

    # ベースフォルダパスの決定
    base_folder = image_type.get_folder_path()
    subfolder_path = os.path.join(base_folder, subfolder_name).replace("\\", "/")

    # サムネイルフォルダの設定
    thumbnail_folder = WITH_SAMPLE_THUMBNAIL_FOLDER if image_type.is_sample else THUMBNAIL_FOLDER

    # サブフォルダ内の画像ファイルの一覧を取得
    image_files = []
    target_path = subfolder_path + thumbnail_folder

    if os.path.exists(target_path):
        for root, dirs, files in os.walk(target_path):
            files.sort(key=lambda f: extract_number(f))
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    image_files.append(file)
    else:
        abort(404)

    if not image_files:
        abort(404)

    base_folder = os.path.basename(base_folder)

    # サブフォルダ内のjsonファイル（画像生成時のプロンプト）の内容を取得
    prompts = []
    json_files = []  # JSONファイルのパスを保存するリスト

    # 翻訳対象のカテゴリを動的に取得
    translate_categories = []
    translate_json_dir = os.path.join('static', 'translate_json')
    if os.path.exists(translate_json_dir):
        for file in os.listdir(translate_json_dir):
            if file.endswith('.json'):
                category_name = os.path.splitext(file)[0]
                translate_categories.append(category_name)

    for f in sorted(os.scandir(subfolder_path), key=lambda x: x.name.lower()):
        if f.is_file() and f.name.lower().endswith(('.json')):
            json_files.append(f.path)  # JSONファイルのパスを保存
            with open(f.path, 'r', encoding='utf-8') as json_file:
                prompt = create_prompt(json_file, translate_categories)
                if prompt:
                    prompts.append(prompt)

    # モデル情報の取得
    model_name = None
    model_credit = None

    # JSONファイルが存在する場合、最初のファイルからモデル情報を取得
    if json_files:
        model_name = get_model_info_from_json(json_files[0])
        if model_name:
            # モデル名に対応するクレジット情報を取得
            model_credit = get_model_credit_info(model_name)

    # 選択された大項目および中項目に対する小項目がすべて非表示かどうかを確認
    all_subcategories_hidden = are_all_subcategories_hidden(style, category, config)

    # テンプレートに渡すデータを設定
    template_data = {
        'subfolder_name': subfolder_name,
        'base_folder': base_folder,
        'thumbnail_folder': thumbnail_folder,
        'image_files': image_files,
        'image_name': image_files[0],
        'is_sample': image_type.is_sample,
        'page': page,
        'prompts': prompts,
        'image_pattern_category': style,
        'image_pattern_subcategory': category,
        'image_pattern_type': subcategory,
        'options': options,
        # モデル情報を追加
        'model_name': model_name,
        'model_credit': model_credit,
        # 設定ファイルから取得したデータを追加
        'styles': get_styles(config),
        'categories': get_categories(style, config),
        'subcategories': get_subcategories(style, category, config) if not all_subcategories_hidden else [],
        'has_subcategories': not all_subcategories_hidden
    }

    return render_template('subfolders.html', **template_data)

@app.route('/user_policy/')
def index_user_policy():
    return render_template('user_policy.html')

@app.route('/images/<path:image_file>')
def get_image(image_file):
    # 末尾のスラッシュを削除
    image_file = image_file.rstrip('/')

    # パスの各部分を取得（例：20231124-17-1409855962/thumbnail/00000-1409855962-thumbnail.png）
    path_parts = image_file.split('/')
    folder_name = path_parts[0]  # 例：20231124-17-1409855962

    # サブフォルダ以降のパスを結合して画像名を取得
    image_path = '/'.join(path_parts[2:]) if len(path_parts) > 2 else path_parts[-1]
    # サブフォルダを取得(パスのうち、最初のディレクトリと最後のファイル名の間を取得する。パスが最初のディレクトリ直下なら空文字を返す。)
    subfolder_name = '/' + '/'.join(path_parts[1:-1]) if len(path_parts) > 2 else ''

    # 新しいフォルダ構造で画像を探す
    possible_paths = []

    # 設定ファイルから表示可能なスタイル、カテゴリ、サブカテゴリを取得
    config = g.config
    styles = [style["id"] for style in get_styles(config)]

    # 各スタイルに対して表示可能なカテゴリを取得
    for style in styles:
        categories = [category["id"] for category in get_categories(style, config)]

        # 各カテゴリに対して表示可能なサブカテゴリを取得
        for category in categories:
            subcategories = [subcategory["id"] for subcategory in get_subcategories(style, category, config)]

            # サブカテゴリがない場合はカテゴリのみのパスを追加
            if not subcategories:
                possible_paths.append(f"sync_images/{style}/{category}/{folder_name}{subfolder_name}/{image_path}")
            else:
                # 各サブカテゴリに対してパスを追加
                for subcategory in subcategories:
                    possible_paths.append(f"sync_images/{style}/{category}/{subcategory}/{folder_name}{subfolder_name}/{image_path}")

    print(f"Looking for image in paths: {possible_paths}")  # デバッグ用

    # 存在するパスを探す
    for full_path in possible_paths:
        if os.path.exists(os.path.join('./static', full_path)):
            print(f"Found image at: {full_path}")
            return send_from_directory('./static', full_path)

    # 画像が見つからない場合は404
    abort(404)

@app.route('/sitemap.xml')
def get_sitemap():
    # サイトマップを表示
    return send_from_directory('./', 'sitemap.xml')

@app.route('/bootstrap/')
def index_bootstrap():
    return render_template('bootstrap.html')

@app.errorhandler(404)
def page_not_found(e):
    # 設定ファイルを取得
    config = g.config
    # 表示可能な画像一覧への誘導用HTMLを表示
    return redirect_to_image_list(config)

# 表示順テスト用のルート
@app.route('/test_display_order/')
@app.route('/test_display_order/<style_id>/')
@app.route('/test_display_order/<style_id>/<category_id>/')
def test_display_order(style_id=None, category_id=None):
    """表示順の制御機能をテストするためのルート"""
    config = g.config

    # すべてのスタイル（表示順でソート済み）
    styles = get_styles(config)

    # 選択されたスタイル
    selected_style = None
    if style_id:
        selected_style = get_style_by_id(style_id, config)

    # 選択されたカテゴリ
    selected_category = None
    if selected_style and category_id:
        selected_category = get_category_by_id(category_id, config)

    # カテゴリとサブカテゴリの取得
    categories = []
    subcategories = []

    if selected_style:
        categories = get_categories(selected_style["id"], config)

        if selected_category:
            subcategories = get_subcategories(selected_style["id"], selected_category["id"], config)

    # 最初の表示可能なアイテム
    first_style = get_first_visible_style(config)
    first_category = None
    first_subcategory = None

    if first_style:
        first_category = get_first_visible_category(first_style["id"], config)

        if first_category:
            first_subcategory = get_first_visible_subcategory(first_style["id"], first_category["id"], config)

    return render_template('test_display_order.html',
                          styles=styles,
                          selected_style=selected_style,
                          selected_category=selected_category,
                          categories=categories,
                          subcategories=subcategories,
                          first_style=first_style,
                          first_category=first_category,
                          first_subcategory=first_subcategory)

# 設定ファイルからスタイル情報を取得する関数
def get_style_by_id(style_id, config=None):
    """
    指定されたIDのスタイルを取得する関数

    Args:
        style_id (str): スタイルID
        config (dict, optional): 設定情報。Noneの場合はg.configを使用。

    Returns:
        dict or None: スタイル情報。見つからない場合はNone。
    """
    if config is None:
        config = g.config

    for style in config.get("styles", []):
        if style.get("id") == style_id and style.get("visible", True):
            return style
    return None

# 設定ファイルからカテゴリ情報を取得する関数
def get_category_by_id(category_id, config=None):
    """
    指定されたIDのカテゴリを取得する関数

    Args:
        category_id (str): カテゴリID
        config (dict, optional): 設定情報。Noneの場合はg.configを使用。

    Returns:
        dict or None: カテゴリ情報。見つからない場合はNone。
    """
    if config is None:
        config = g.config

    for category in config.get("categories", []):
        if category.get("id") == category_id and category.get("visible", True):
            return category
    return None

# 設定ファイルからサブカテゴリ情報を取得する関数
def get_subcategory_by_id(subcategory_id, config=None):
    """
    指定されたIDのサブカテゴリを取得する関数

    Args:
        subcategory_id (str): サブカテゴリID
        config (dict, optional): 設定情報。Noneの場合はg.configを使用。

    Returns:
        dict or None: サブカテゴリ情報。見つからない場合はNone。
    """
    if config is None:
        config = g.config

    for subcategory in config.get("subcategories", []):
        if subcategory.get("id") == subcategory_id and subcategory.get("visible", True):
            return subcategory
    return None

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')