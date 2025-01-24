import os
import re
from flask import Flask, render_template, send_from_directory, request, abort, g

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

def get_subfolders(folder_path, page, is_sample=True, is_male=False, is_transparent_background=False, is_selfie=False, is_background=False):
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
            # /male,/background が含まれている場合はもう1階層遡る
            if is_background or is_male:
                is_dig = True

            # サブフォルダの文字列にsample, sample-thumbnail, thumbnail, half_resolution が含まれた場合は除外
            if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER, WITH_SAMPLE_THUMBNAIL_FOLDER, THUMBNAIL_FOLDER, HALF_RESOLUTION_FOLDER]):
                continue

            # 背景画像を表示するか否かに応じてフォルダーをスキップ
            if is_background == False:
                if any(x in subfolder_path for x in [BACKGROUND_FOLDER_PREFIX]):
                    continue
            if is_background and BACKGROUND_FOLDER_PREFIX not in subfolder_path:
                continue

            # 男性画像を表示するか否かに応じてフォルダーをスキップ
            if is_male == False:
                if any(x in subfolder_path for x in [MALE_FOLDER_PREFIX]):
                    continue
            if is_male and MALE_FOLDER_PREFIX not in subfolder_path:
                continue

            if is_transparent_background == False:
                if any(x in subfolder_path for x in [TRANSPARENT_BACKGROUND_FOLDER_PREFIX]):
                    continue
            if is_transparent_background and TRANSPARENT_BACKGROUND_FOLDER_PREFIX not in subfolder_path:
                continue

            if is_selfie == False:
                if any(x in subfolder_path for x in [SELFIE_FOLDER_PREFIX]):
                    continue
            if is_selfie and SELFIE_FOLDER_PREFIX not in subfolder_path:
                continue

            if is_sample:
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
    add_param = '?'

    # サンプル画像か否か
    is_sample = SAMPLE_IMAGE_FLAG

    # URLのパラメータから is_transparent を取得
    is_transparent_background_get_param = request.args.get('is_transparent', 'false')
    is_transparent_background = False
    is_transparent_background_set_param = ""

    # URLのパラメータから is_selfie を取得
    is_selfie_get_param = request.args.get('is_selfie', 'false')
    is_selfie = False
    is_selfie_set_param = ""

    print("request.args: " + str(request.args))

    # is_transparent パラメータが"true"の場合、Trueをセット
    if is_transparent_background_get_param.lower() == 'true':
        is_transparent_background = True
        is_transparent_background_set_param = "&is_transparent=true"

    # is_selfie パラメータが"true"の場合、Trueをセット
    if is_selfie_get_param.lower() == 'true':
        is_selfie = True
        is_selfie_set_param = "&is_selfie=true"

    # 現在のページ番号を取得
    page = request.args.get('page', default=1, type=int)

    # サブフォルダのリストを取得
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, is_sample, False, is_transparent_background, is_selfie)

    print(f"total_count: {total_count}")

    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)
    return render_template('index.html', subfolder_images=subfolder_images, pagination_info=pagination_info, add_param=add_param, is_male=False, is_transparent_background=is_transparent_background, is_transparent_background_set_param=is_transparent_background_set_param, is_selfie=is_selfie, is_selfie_set_param=is_selfie_set_param)

@app.route('/male/')
def index_male():
    add_param = '?'

    # サンプル画像か否か
    is_sample = SAMPLE_IMAGE_FLAG

    # URLのパラメータから is_transparent を取得
    is_transparent_background_get_param = request.args.get('is_transparent', 'false')
    is_transparent_background = False
    is_transparent_background_set_param = ""

    # URLのパラメータから is_selfie を取得
    is_selfie_get_param = request.args.get('is_selfie', 'false')
    is_selfie = False
    is_selfie_set_param = ""

    # is_transparent パラメータが"true"の場合、Trueをセット
    if is_transparent_background_get_param.lower() == 'true':
        is_transparent_background = True
        is_transparent_background_set_param = "&is_transparent=true"
    
    # is_selfie パラメータが"true"の場合、Trueをセット
    if is_selfie_get_param.lower() == 'true':
        is_selfie = True
        is_selfie_set_param = "&is_selfie=true"

    # 現在のページ番号を取得
    page = request.args.get('page', default=1, type=int)

    # サブフォルダのリストを取得
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, is_sample, True, is_transparent_background, is_selfie)

    print(f"total_count: {total_count}")

    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)
    return render_template('index.html', subfolder_images=subfolder_images, pagination_info=pagination_info, add_param=add_param, is_male=True, is_transparent_background=is_transparent_background, is_transparent_background_set_param=is_transparent_background_set_param, is_selfie=is_selfie, is_selfie_set_param=is_selfie_set_param)

@app.route('/background/')
def index_background():
    add_param = '?'

    # サンプル画像か否か
    is_sample = SAMPLE_IMAGE_FLAG

    # 現在のページ番号を取得
    page = request.args.get('page', default=1, type=int)

    # サブフォルダのリストを取得
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, is_sample, False, False, False, True)

    print(f"total_count: {total_count}")

    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)
    return render_template('index.html', subfolder_images=subfolder_images, pagination_info=pagination_info, add_param=add_param, is_male=False, is_transparent_background=False, is_transparent_background_set_param="", is_selfie=False, is_selfie_set_param="", is_background=True, is_background_set_param="&is_background=true")

@app.route('/subfolders/<subfolder_name>/')
def subfolder_images(subfolder_name):
    add_param = '?'
    subfolder_path = os.path.join(IMAGE_FOLDER, subfolder_name).replace("\\", "/")
    thumbnail_folder = THUMBNAIL_FOLDER
    # サンプル画像か否か
    is_sample = SAMPLE_IMAGE_FLAG
    is_male_get_param = request.args.get('is_male', 'false')
    is_male = False
    is_transparent_background = False
    is_transparent_background_get_param = request.args.get('is_transparent', 'false')
    is_selfie = False
    is_selfie_get_param = request.args.get('is_selfie', 'false')
    is_background = False
    is_background_get_param = request.args.get('is_background', 'false')
    page = request.args.get('page', 1)

    # is_sampleパラメータが"false"の場合、Falseをセット
    if is_sample:
        subfolder_path = subfolder_path + WITH_SAMPLE_THUMBNAIL_FOLDER
        thumbnail_folder = WITH_SAMPLE_THUMBNAIL_FOLDER
    else:
        subfolder_path = subfolder_path + THUMBNAIL_FOLDER
        thumbnail_folder = THUMBNAIL_FOLDER

    # page数もパラメータで保持(戻るボタンに必要)
    add_param = add_param + "&page=" + str(page)

    # is_maleパラメータが"true"の場合、Trueをセット
    if is_male_get_param.lower() == 'true':
        is_male = True
        add_param = add_param + "&is_male=True"
    else:
        add_param = add_param + "&is_male=False"

    # is_transparent パラメータが"true"の場合、Trueをセット
    if is_transparent_background_get_param.lower() == 'true':
        add_param = add_param + "&is_transparent=True"
        is_transparent_background = True
    else:
        add_param = add_param + "&is_transparent=False"

    # is_selfie パラメータが"true"の場合、Trueをセット
    if is_selfie_get_param.lower() == 'true':
        add_param = add_param + "&is_selfie=True"
        is_selfie = True
    else:
        add_param = add_param + "&is_selfie=False"

    # is_background パラメータが"true"の場合、Trueをセット
    if is_background_get_param.lower() == 'true':
        add_param = add_param + "&is_background=True"
        is_background = True
    else:
        add_param = add_param + "&is_background=False"

    # サブフォルダ内の画像ファイルの一覧を取得
    image_files = []
    for root, dirs, files in os.walk(subfolder_path):
        # ファイル名の先頭の数字をキーにしてソート
        files.sort(key=lambda f: extract_number(f))
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_files.append(file)

    return render_template('subfolders.html', subfolder_name=subfolder_name, thumbnail_folder=thumbnail_folder, image_files=image_files, is_sample=is_sample, add_param=add_param, page=page, is_male=is_male, is_transparent_background=is_transparent_background, is_selfie=is_selfie, is_background=is_background)

@app.route('/user_policy/')
def index_user_policy():
    return render_template('user_policy.html')

@app.route('/images/<path:image_file>/')
def get_image(image_file):

    # サンプル画像か否か
    is_sample = SAMPLE_IMAGE_FLAG

    # is_sampleパラメータが"false"の場合
    if is_sample:
        # image_file の文字列内に`sample`が含まれていなかった場合404エラーを返す
        if 'sample' not in image_file:
            abort(404)

    # 原寸大の画像を表示
    return send_from_directory(IMAGE_FOLDER, image_file)

@app.route('/sitemap.xml')
def get_sitemap():
    # サイトマップを表示
    return send_from_directory('./', 'sitemap.xml')

@app.route('/bootstrap/')
def index_bootstrap():

    return render_template('bootstrap.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')