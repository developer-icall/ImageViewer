import os
from flask import Flask, render_template, send_from_directory, request, abort

app = Flask(__name__)

# 画像フォルダのパス
IMAGE_FOLDER = './static/sync_images'

# サムネイル用画像の保存先フォルダのパス
THUMBNAIL_FOLDER = "/thumbnail"

# Sample文字が入っている等倍画像の保存先フォルダのパス
WITH_SAMPLE_TEXT_FOLDER = "/sample"

# Sample文字が入っていサムネイル用画像の保存先フォルダのパス
WITH_SAMPLE_THUMBNAIL_FOLDER = "/sample-thumbnail"

# 半分の解像度の画像保存先フォルダパス
HALF_RESOLUTION_FOLDER = "/half-resolution"

# 1ページ当たりの表示件数
INDEX_PER_PAGE = 20

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
        for file in files:
            if file.lower().endswith(('.png')):
                return os.path.join(root, file).replace("\\", "/")
    return None

def get_subfolders(folder_path, page, is_sample=True):
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
            # サブフォルダの文字列にsample, sample-thumbnail, thumbnail, half_resolution が含まれた場合は除外
            if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER, WITH_SAMPLE_THUMBNAIL_FOLDER, THUMBNAIL_FOLDER, HALF_RESOLUTION_FOLDER]):
                continue
            if is_sample:
                first_image = get_first_image(subfolder_path + WITH_SAMPLE_THUMBNAIL_FOLDER)
            else:
                if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER, WITH_SAMPLE_THUMBNAIL_FOLDER, THUMBNAIL_FOLDER]):
                    continue
                first_image = get_first_image(subfolder_path + THUMBNAIL_FOLDER)
            if first_image:
                if index >= start_index and index < end_index:
                    subfolders.append((dir, first_image))
            index = index + 1
    return subfolders, index

@app.route('/')
def index():
    # URLのパラメータからis_sampleを取得
    is_sample_get_param = request.args.get('hidden_secret_param_is_sample', 'true')
   
    # is_sampleパラメータが"false"の場合、Falseをセット
    if is_sample_get_param.lower() == 'false':
        is_sample = False
        is_sample_param = "?hidden_secret_param_is_sample=False"
    else:
        is_sample = True
        # ダミーパラメータをセット(以降に追加するパラメータを`&xxxx`の形式で追加できるようにするためと、パラメータ解析防止のハッタリのため)
        is_sample_param = "?Q=866Tvdnm9f1iuWn6opQZ"

    # 現在のページ番号を取得
    page = request.args.get('page', default=1, type=int)

    # サブフォルダのリストを取得
    subfolder_images, total_count = get_subfolders(IMAGE_FOLDER, page, is_sample)

    print(f"total_count: {total_count}")

    pagination_info = get_pagination_info(total_count, INDEX_PER_PAGE)
    return render_template('index.html', subfolder_images=subfolder_images, pagination_info=pagination_info, is_sample_param=is_sample_param)

@app.route('/subfolders/<subfolder_name>/')
def subfolder_images(subfolder_name):
    subfolder_path = os.path.join(IMAGE_FOLDER, subfolder_name).replace("\\", "/")
    thumbnail_folder = THUMBNAIL_FOLDER
    # URLのパラメータからis_sampleを取得
    is_sample_get_param = request.args.get('hidden_secret_param_is_sample', 'true')
    page = request.args.get('page', 1)
    
    # is_sampleパラメータが"false"の場合、Falseをセット
    if is_sample_get_param.lower() == 'false':
        is_sample = False
        is_sample_param = "?hidden_secret_param_is_sample=False"
        subfolder_path = subfolder_path + THUMBNAIL_FOLDER
        thumbnail_folder = THUMBNAIL_FOLDER
    else:
        is_sample = True
        # ダミーパラメータをセット(以降に追加するパラメータを`&xxxx`の形式で追加できるようにするためと、パラメータ解析防止のハッタリのため)
        is_sample_param = "?Q=866Tvdnm9f1iuWn6opQZ"
        subfolder_path = subfolder_path + WITH_SAMPLE_THUMBNAIL_FOLDER
        thumbnail_folder = WITH_SAMPLE_THUMBNAIL_FOLDER

    print(subfolder_path)
    # サブフォルダ内の画像ファイルの一覧を取得
    image_files = [f.name for f in os.scandir(subfolder_path) if f.is_file() and f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    return render_template('subfolders.html', subfolder_name=subfolder_name, thumbnail_folder=thumbnail_folder, image_files=image_files, is_sample=is_sample, is_sample_param=is_sample_param, page=page)

@app.route('/images/<path:image_file>/')
def get_image(image_file):

    # URLのパラメータからis_sampleを取得
    is_sample_get_param = request.args.get('hidden_secret_param_is_sample', 'true')
    
    # is_sampleパラメータが"false"の場合、Falseをセット
    if is_sample_get_param.lower() == 'false':
        is_sample = False
    else:
        is_sample = True
        # image_file の文字列内に`sample`が含まれていなかった場合404エラーを返す
        if 'sample' not in image_file:
            abort(404)

    # 原寸大の画像を表示
    return send_from_directory(IMAGE_FOLDER, image_file)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')