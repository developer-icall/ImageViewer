import os
import re
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import Flask, render_template, send_from_directory, request, abort, g, redirect, make_response, send_file
import zipfile
from io import BytesIO
from flask_caching import Cache

app = Flask(__name__)

# キャッシュ設定
cache = Cache(app, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache',
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5分
    'CACHE_THRESHOLD': 1000  # キャッシュエントリの最大数
})

# キャッシュディレクトリの作成
CACHE_DIR = 'cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# ログ設定
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# アクセスログの設定
access_logger = logging.getLogger('access_logger')
access_logger.setLevel(logging.INFO)
access_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'access.log'),
    maxBytes=1024 * 1024,  # 1MB
    backupCount=10
)
access_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(remote_addr)s - "%(method)s %(url)s" %(status)s - %(response_time).2fms'
))
access_logger.addHandler(access_handler)

# エラーログの設定
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
error_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'error.log'),
    maxBytes=1024 * 1024,  # 1MB
    backupCount=10
)
error_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s\n'
    'Path: %(url)s\n'
    'IP: %(remote_addr)s\n'
    'User Agent: %(user_agent)s\n'
    '%(traceback)s'
))
error_logger.addHandler(error_handler)

# アクセスログを記録するミドルウェア
@app.before_request
def start_timer():
    g.start = datetime.now()

@app.after_request
def log_request(response):
    if hasattr(g, 'start'):
        total_time = (datetime.now() - g.start).total_seconds() * 1000

        access_logger.info('', extra={
            'remote_addr': request.remote_addr,
            'method': request.method,
            'url': request.full_path,
            'status': response.status_code,
            'response_time': total_time
        })
    return response

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

# 背景画像保存先フォルダパスの prefix
BACKGROUND_FOLDER_PREFIX = "-background"

# 男性画像保存先フォルダパスの prefix
MALE_FOLDER_PREFIX = "-men"

# 背景透過画像保存先のフォルダパスの prefix
TRANSPARENT_BACKGROUND_FOLDER_PREFIX = "-transparent"

# セルフィー画像保存先のフォルダパスの prefix
SELFIE_FOLDER_PREFIX = "-selfie"

# 1ページ当たりの表示件数
INDEX_PER_PAGE = 12

# 新しい画像フォルダのパス定義を追加
STYLE_FOLDERS = {
    'realistic': './static/sync_images/realistic',
    'illustration': './static/sync_images/illustrationillustration'
}

# 画像タイプを定義するクラスを追加
class ImageType:
    def __init__(self, style_type=None, category=None, subcategory=None):
        self.style_type = style_type
        self.category = category
        self.subcategory = subcategory

    def get_folder_path(self):
        base_path = STYLE_FOLDERS.get(self.style_type)
        if not base_path:
            return None

        folder_path = base_path
        if self.category:
            folder_path = os.path.join(folder_path, self.category)
        if self.subcategory:
            folder_path = os.path.join(folder_path, self.subcategory)

        return folder_path.replace("\\", "/")

# テンプレートに渡す定数
@app.before_request
def before_request():
    g.domain_name = DOMAIN_NAME  # ドメイン
    g.site_name = DOMAIN_NAME  # サイト名

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
        files.sort()
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # フォルダ構造からスタイルタイプを抽出
                path_parts = subfolder_path.split(os.sep)
                style_type = path_parts[-4] if len(path_parts) >= 4 else ''

                # 画像のURLパスを構築
                folder_name = os.path.basename(os.path.dirname(os.path.dirname(subfolder_path)))
                return f"/images/{style_type}/{folder_name}/thumbnail/{file}"
    return None

def get_subfolders(folder_path, page, image_type):
    if not os.path.exists(folder_path):
        return [], 0

    subfolders = []
    start_index = (page - 1) * INDEX_PER_PAGE
    end_index = start_index + INDEX_PER_PAGE
    index = 0

    for root, dirs, files in os.walk(folder_path):
        dirs.sort()
        for dir in dirs:
            subfolder_path = os.path.join(root, dir).replace("\\", "/")

            # サムネイル関連のフォルダは除外
            if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER,
                                               WITH_SAMPLE_THUMBNAIL_FOLDER,
                                               THUMBNAIL_FOLDER,
                                               HALF_RESOLUTION_FOLDER]):
                continue

            first_image = get_first_image(subfolder_path +
                         (WITH_SAMPLE_THUMBNAIL_FOLDER if SAMPLE_IMAGE_FLAG else THUMBNAIL_FOLDER))

            if first_image and index >= start_index and index < end_index:
                subfolders.append((dir, first_image))
            index += 1

    return subfolders, index

def extract_number(filename):
    match = re.match(r"(\d+)", filename)
    return int(match.group(1)) if match else float('inf')

@app.route('/')
def index():
    return redirect('/brav/female/')

@app.route('/brav/female/')
def brav_female():
    # 古いis_sampleパラメータは使用しない
    image_type = ImageType(
        style_type='realistic',
        category='female'
    )

    page = request.args.get('page', default=1, type=int)
    folder_path = image_type.get_folder_path()

    subfolder_images, total_count = get_subfolders(folder_path, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('subfolders.html',
                         style_type='realistic',
                         category='female',
                         category_name='女性',
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info)

@app.route('/brav/female/transparent/')
def brav_female_transparent():
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_male=False,
        is_transparent_background=True,
        is_selfie=False
    )
    page = request.args.get('page', default=1, type=int)
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('index.html',
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info,
                         is_male=False,
                         is_transparent_background=True,
                         is_selfie=False,
                         is_rpgicon=False,
                         is_background=False)

@app.route('/brav/female/selfie/')
def brav_female_selfie():
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_male=False,
        is_transparent_background=False,
        is_selfie=True
    )
    page = request.args.get('page', default=1, type=int)
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('index.html',
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info,
                         is_male=False,
                         is_transparent_background=False,
                         is_selfie=True,
                         is_rpgicon=False,
                         is_background=False)

@app.route('/brav/male/')
def brav_male():
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_male=True,
        is_transparent_background=False,
        is_selfie=False
    )
    page = request.args.get('page', default=1, type=int)
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('index.html',
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info,
                         is_male=True,
                         is_transparent_background=False,
                         is_selfie=False,
                         is_rpgicon=False,
                         is_background=False)

@app.route('/brav/male/transparent/')
def brav_male_transparent():
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_male=True,
        is_transparent_background=True,
        is_selfie=False
    )
    page = request.args.get('page', default=1, type=int)
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('index.html',
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info,
                         is_male=True,
                         is_transparent_background=True,
                         is_selfie=False,
                         is_rpgicon=False,
                         is_background=False)

@app.route('/brav/male/selfie/')
def brav_male_selfie():
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_male=True,
        is_transparent_background=False,
        is_selfie=True
    )
    page = request.args.get('page', default=1, type=int)
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('index.html',
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info,
                         is_male=True,
                         is_transparent_background=False,
                         is_selfie=True,
                         is_rpgicon=False,
                         is_background=False)

@app.route('/rpgicon/')
def rpgicon():
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_rpgicon=True
    )
    page = request.args.get('page', default=1, type=int)
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('index.html',
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info,
                         is_male=False,
                         is_transparent_background=False,
                         is_selfie=False,
                         is_rpgicon=True,
                         is_background=False)

@app.route('/background/')
def background():
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_background=True
    )
    page = request.args.get('page', default=1, type=int)
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('index.html',
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info,
                         is_male=False,
                         is_transparent_background=False,
                         is_selfie=False,
                         is_rpgicon=False,
                         is_background=True)

@app.route('/brav/<gender>/subfolders/<subfolder_name>/')
@app.route('/brav/<gender>/<option>/subfolders/<subfolder_name>/')
@app.route('/<category>/subfolders/<subfolder_name>/')
def subfolder_images_new(subfolder_name, gender=None, option=None, category=None):
    # カテゴリーからパラメータを解析
    is_male = gender == 'male' if gender else False
    is_transparent_background = option == 'transparent' if option else False
    is_selfie = option == 'selfie' if option else False
    is_background = category == 'background' if category else False
    is_rpgicon = category == 'rpgicon' if category else False

    page = request.args.get('page', 1)

    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_male=is_male,
        is_transparent_background=is_transparent_background,
        is_selfie=is_selfie,
        is_background=is_background,
        is_rpgicon=is_rpgicon
    )

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

    return render_template('subfolders.html',
                         subfolder_name=subfolder_name,
                         base_folder=base_folder,
                         thumbnail_folder=thumbnail_folder,
                         image_files=image_files,
                         image_name=image_files[0],
                         is_sample=image_type.is_sample,
                         page=page,
                         is_male=is_male,
                         is_transparent_background=is_transparent_background,
                         is_selfie=is_selfie,
                         is_background=is_background,
                         is_rpgicon=is_rpgicon)

@app.route('/user_policy/')
def index_user_policy():
    return render_template('user_policy.html')

@app.route('/images/<style_type>/<path:image_file>')
@cache.cached(timeout=3600, key_prefix=lambda: f'view/images/{style_type}/{image_file}')
def get_image(style_type, image_file):
    # 末尾のスラッシュを削除
    image_file = image_file.rstrip('/')

    # パスの各部分を取得
    path_parts = image_file.split('/')
    folder_name = path_parts[0]

    # thumbnailフォルダ以降のパスを結合
    image_path = '/'.join(path_parts[2:]) if len(path_parts) > 2 else path_parts[-1]

    # スタイルタイプに応じたフォルダパスを構築
    base_folder = STYLE_FOLDERS.get(style_type)
    if not base_folder:
        abort(404)

    full_path = os.path.join(base_folder, folder_name,
                            WITH_SAMPLE_THUMBNAIL_FOLDER if SAMPLE_IMAGE_FLAG else THUMBNAIL_FOLDER,
                            image_path)

    if os.path.exists(full_path):
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))

    abort(404)

@app.route('/sitemap.xml')
@cache.cached(timeout=3600)
def sitemap():
    """サイトマップを生成して返す"""
    urls = generate_sitemap()

    response = make_response(
        render_template('sitemap.xml', urls=urls, domain_name=DOMAIN_NAME)
    )
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/bootstrap/')
def index_bootstrap():

    return render_template('bootstrap.html')

# スタイルタイプの定義
STYLE_TYPES = {
    'realistic': 'リアルテイスト画像',
    'illustration': 'ゲーム、イラスト風画像'
}

# カテゴリーの定義
CATEGORIES = {
    'realistic': {
        'female': '女性',
        'male': '男性',
        'animal': '動物'
    },
    'illustration': {
        'female': '女性',
        'male': '男性',
        'animal': '動物',
        'background': '背景',
        'rpg_icon': 'RPGアイコン',
        'vehicle': '乗り物',
        'other': 'その他'
    }
}

# サブカテゴリーの定義
SUBCATEGORIES = {
    'female': {
        'normal': '通常画像',
        'transparent': '透明背景画像',
        'selfie': 'セルフィー画像'
    },
    'male': {
        'normal': '通常画像',
        'transparent': '透明背景画像',
        'selfie': 'セルフィー画像'
    },
    'animal': {
        'dog': '犬',
        'cat': '猫',
        'bird': '鳥',
        'fish': '魚',
        'other': 'その他'
    },
    'background': {
        'nature': '自然',
        'city': '都市',
        'sea': '海',
        'sky': '空',
        'other': 'その他'
    },
    'rpg_icon': {
        'weapon': '武器・防具',
        'monster': 'モンスター',
        'other': 'その他'
    },
    'vehicle': {
        'car': '車',
        'ship': '船',
        'airplane': '飛行機',
        'other': 'その他'
    }
}

@app.route('/style/<style_type>')
@cache.cached(timeout=300, key_prefix=lambda: f'view/style/{style_type}')
def show_style(style_type):
    if style_type not in STYLE_TYPES:
        abort(404)

    image_type = ImageType(style_type=style_type)
    page = request.args.get('page', default=1, type=int)
    folder_path = image_type.get_folder_path()

    subfolder_images, total_count = get_subfolders(folder_path, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('index.html',
                         style_type=style_type,
                         style_name=STYLE_TYPES[style_type],
                         categories=CATEGORIES[style_type],
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info)

@app.route('/style/<style_type>/<category>')
@cache.cached(timeout=300, key_prefix=lambda: f'view/style/{style_type}/{category}')
def show_category(style_type, category):
    if style_type not in STYLE_TYPES or category not in CATEGORIES[style_type]:
        abort(404)

    image_type = ImageType(style_type=style_type, category=category)
    page = request.args.get('page', default=1, type=int)
    folder_path = image_type.get_folder_path()

    # カテゴリーに対応するサブカテゴリーを取得
    subcategories = SUBCATEGORIES.get(category, {})

    # カテゴリー配下の画像を取得
    subfolder_images, total_count = get_subfolders(folder_path, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('subfolders.html',
                         style_type=style_type,
                         category=category,
                         category_name=CATEGORIES[style_type][category],
                         subcategories=subcategories,
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info)

@app.route('/style/<style_type>/<category>/<subcategory>')
@cache.cached(timeout=300, key_prefix=lambda: f'view/style/{style_type}/{category}/{subcategory}')
def show_subcategory(style_type, category, subcategory):
    if (style_type not in STYLE_TYPES or
        category not in CATEGORIES[style_type] or
        subcategory not in SUBCATEGORIES.get(category, {})):
        abort(404)

    image_type = ImageType(style_type=style_type,
                          category=category,
                          subcategory=subcategory)
    page = request.args.get('page', default=1, type=int)
    folder_path = image_type.get_folder_path()

    # サブカテゴリー配下の画像を取得
    subfolder_images, total_count = get_subfolders(folder_path, page, image_type)
    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)

    return render_template('images.html',
                         style_type=style_type,
                         category=category,
                         subcategory=subcategory,
                         subcategory_name=SUBCATEGORIES[category][subcategory],
                         subfolder_images=subfolder_images,
                         pagination_info=pagination_info)

def generate_sitemap():
    """動的にサイトマップを生成する関数"""
    urls = []

    # スタイルページ
    for style in STYLE_TYPES:
        urls.append({
            'loc': f'/style/{style}',
            'changefreq': 'daily',
            'priority': '0.8'
        })

        # カテゴリーページ
        for category in CATEGORIES[style]:
            urls.append({
                'loc': f'/style/{style}/{category}',
                'changefreq': 'daily',
                'priority': '0.7'
            })

            # サブカテゴリーページ
            if category in SUBCATEGORIES:
                for subcategory in SUBCATEGORIES[category]:
                    urls.append({
                        'loc': f'/style/{style}/{category}/{subcategory}',
                        'changefreq': 'daily',
                        'priority': '0.6'
                    })

    return urls

@app.route('/download/<style_type>/<category>/<subcategory>/<folder_name>')
def download_images(style_type, category, subcategory, folder_name):
    """画像をZIPファイルとしてダウンロードする"""
    if (style_type not in STYLE_TYPES or
        category not in CATEGORIES[style_type] or
        subcategory not in SUBCATEGORIES.get(category, {})):
        abort(404)

    # フォルダパスの構築
    base_folder = STYLE_FOLDERS.get(style_type)
    if not base_folder:
        abort(404)

    folder_path = os.path.join(base_folder, folder_name)
    if not os.path.exists(folder_path):
        abort(404)

    # ZIPファイルの作成
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 画像ファイルの追加
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # サムネイルやサンプル画像は除外
                    if any(x in root for x in [THUMBNAIL_FOLDER,
                                             WITH_SAMPLE_TEXT_FOLDER,
                                             WITH_SAMPLE_THUMBNAIL_FOLDER]):
                        continue

                    file_path = os.path.join(root, file)
                    arc_name = os.path.basename(file_path)
                    zf.write(file_path, arc_name)

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{folder_name}.zip'
    )

# エラーハンドラ
@app.errorhandler(404)
def page_not_found(e):
    error_logger.error('Page not found', extra={
        'url': request.full_path,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string,
        'traceback': ''
    })
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    import traceback
    error_logger.error('Internal server error', extra={
        'url': request.full_path,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string,
        'traceback': traceback.format_exc()
    })
    return render_template('errors/500.html'), 500

# 既存のエラーハンドラに加えて、その他のエラーもキャッチ
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    error_logger.error(str(e), extra={
        'url': request.full_path,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string,
        'traceback': traceback.format_exc()
    })
    return render_template('errors/500.html'), 500

# 開発環境でもエラーページを表示するための設定
app.config['PROPAGATE_EXCEPTIONS'] = True

# キャッシュを手動でクリアするエンドポイント（管理者用）
@app.route('/admin/clear-cache', methods=['POST'])
def clear_cache():
    try:
        cache.clear()
        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        error_logger.error('Cache clear error', extra={
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        return jsonify({'error': 'Failed to clear cache'}), 500

# キャッシュ制御ミドルウェア
@app.after_request
def add_cache_headers(response):
    # 静的ファイルのキャッシュ設定
    if request.path.startswith('/static/'):
        response.cache_control.public = True
        response.cache_control.max_age = 86400  # 24時間

    # 画像のキャッシュ設定
    elif request.path.startswith('/images/'):
        response.cache_control.public = True
        response.cache_control.max_age = 3600  # 1時間

    # 動的ページのキャッシュ設定
    else:
        response.cache_control.private = True
        response.cache_control.max_age = 300  # 5分

    return response

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')