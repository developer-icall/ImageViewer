import os
import re
from flask import Flask, render_template, send_from_directory, request, abort, g, redirect

app = Flask(__name__)

# ドメイン
DOMAIN_NAME = 'ai-gazou.com'

# 画像フォルダのパス
IMAGE_FOLDER = './static/sync_images'
BRAV_FOLDER = './static/sync_images/brav'
RPGICON_FOLDER = './static/sync_images/RPGIcon'
BACKGROUND_FOLDER = './static/sync_images/background'  # 背景画像用フォルダを追加

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

# 画像タイプを定義するクラスを追加
class ImageType:
    def __init__(self, is_sample=True, is_male=False, is_transparent_background=False,
                 is_selfie=False, is_background=False, is_rpgicon=False):
        self.is_sample = is_sample
        self.is_male = is_male
        self.is_transparent_background = is_transparent_background
        self.is_selfie = is_selfie
        self.is_background = is_background
        self.is_rpgicon = is_rpgicon

    def get_folder_path(self):
        if self.is_background:
            return BACKGROUND_FOLDER  # 背景画像用フォルダを返すように変更
        elif self.is_rpgicon:
            return RPGICON_FOLDER
        else:
            return BRAV_FOLDER

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

def get_first_image(subfolder_path, is_dig=False):
    for root, dirs, files in os.walk(subfolder_path):
        files.sort()  # ファイル名順にソート
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):  # 他の画像形式も含める
                image_path = os.path.join(root, file)
                if is_dig:
                    return "." + image_path
                else:
                    return image_path
    return None

def get_subfolders(folder_path, page, image_type):
    # フォルダパスの決定
    folder_path = image_type.get_folder_path()

    subfolders = []
    start_index = (page - 1) * INDEX_PER_PAGE
    end_index = start_index + INDEX_PER_PAGE
    print(f"start_index: {start_index}")
    print(f"end_index: {end_index}")
    index = 0
    total_count = 0

    for root, dirs, files in os.walk(folder_path):
        dirs.sort()  # フォルダの一覧をABC順にソート
        i = 0
        for dir in dirs:
            subfolder_path = os.path.join(root, dir).replace("\\", "/")

            # ページ階層に合わせて、画像フォルダのパスを調整
            is_dig = False
            # /male が含まれている場合はもう1階層遡る（背景画像の場合は不要）
            if image_type.is_male:
                is_dig = True

            # サブフォルダの文字列にsample, sample-thumbnail, thumbnail, half_resolution が含まれた場合は除外
            if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER, WITH_SAMPLE_THUMBNAIL_FOLDER, THUMBNAIL_FOLDER, HALF_RESOLUTION_FOLDER]):
                continue

            # 背景画像の場合は他のフィルタリングをスキップ
            if not image_type.is_background:
                # 男性画像を表示するか否かに応じてフォルダーをスキップ
                if not image_type.is_male:
                    if any(x in subfolder_path for x in [MALE_FOLDER_PREFIX]):
                        continue
                if image_type.is_male and MALE_FOLDER_PREFIX not in subfolder_path:
                    continue

                if not image_type.is_transparent_background:
                    if any(x in subfolder_path for x in [TRANSPARENT_BACKGROUND_FOLDER_PREFIX]):
                        continue
                if image_type.is_transparent_background and TRANSPARENT_BACKGROUND_FOLDER_PREFIX not in subfolder_path:
                    continue

                if not image_type.is_selfie:
                    if any(x in subfolder_path for x in [SELFIE_FOLDER_PREFIX]):
                        continue
                if image_type.is_selfie and SELFIE_FOLDER_PREFIX not in subfolder_path:
                    continue

            if image_type.is_sample:
                first_image = get_first_image(subfolder_path + WITH_SAMPLE_THUMBNAIL_FOLDER, is_dig)
            else:
                if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER, WITH_SAMPLE_THUMBNAIL_FOLDER, THUMBNAIL_FOLDER]):
                    continue
                first_image = get_first_image(subfolder_path + THUMBNAIL_FOLDER, is_dig)
            if first_image:
                if index >= start_index and index < end_index:
                    subfolders.append((dir, first_image))
            else:
                print(f"first image not found:{subfolder_path}")
            index = index + 1
    return subfolders, index

def extract_number(filename):
    match = re.match(r"(\d+)", filename)
    return int(match.group(1)) if match else float('inf')

@app.route('/')
def index():
    return redirect('/brav/female/')

@app.route('/brav/female/')
def brav_female():
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_male=False,
        is_transparent_background=False,
        is_selfie=False
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
                         is_background=False)

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

@app.route('/<path:category>/subfolders/<subfolder_name>/')
def subfolder_images_new(category, subfolder_name):
    # カテゴリーからパラメータを解析
    is_male = 'male' in category
    is_transparent_background = 'transparent' in category
    is_selfie = 'selfie' in category
    is_background = category == 'background'
    is_rpgicon = category == 'rpgicon'
    
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

@app.route('/images/<path:image_file>/')
def get_image(image_file):
    # サンプル画像か否か
    is_sample = SAMPLE_IMAGE_FLAG

    # URLパラメータを取得
    is_male = request.args.get('is_male', 'false').lower() == 'true'
    is_transparent_background = request.args.get('is_transparent', 'false').lower() == 'true'
    is_selfie = request.args.get('is_selfie', 'false').lower() == 'true'
    is_background = request.args.get('is_background', 'false').lower() == 'true'
    is_rpgicon = request.args.get('is_rpgicon', 'false').lower() == 'true'

    # 画像タイプを作成
    image_type = ImageType(
        is_sample=SAMPLE_IMAGE_FLAG,
        is_male=is_male,
        is_transparent_background=is_transparent_background,
        is_selfie=is_selfie,
        is_background=is_background,
        is_rpgicon=is_rpgicon
    )

    # パスの各部分を取得
    path_parts = image_file.split('/')
    subfolder_name = path_parts[0]
    image_name = path_parts[-1]

    # サムネイルフォルダの設定
    if is_sample:
        thumbnail_folder = WITH_SAMPLE_THUMBNAIL_FOLDER
    else:
        thumbnail_folder = THUMBNAIL_FOLDER

    # 完全なパスを構築（static/sync_imagesからの相対パス）
    full_path = f"{os.path.basename(image_type.get_folder_path())}/{subfolder_name}{thumbnail_folder}/{image_name}".replace('\\', '/')

    print(f"full_path: {full_path}")
    # 原寸大の画像を表示（ベースディレクトリはIMAGE_FOLDERの親ディレクトリ）
    return send_from_directory('./static', f"sync_images/{full_path}")

@app.route('/sitemap.xml')
def get_sitemap():
    # サイトマップを表示
    return send_from_directory('./', 'sitemap.xml')

@app.route('/bootstrap/')
def index_bootstrap():

    return render_template('bootstrap.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')