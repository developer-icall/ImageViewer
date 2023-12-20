import os
from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__)

# 画像フォルダのパス
IMAGE_FOLDER = './static/sync_images'

# サムネイル用画像の保存先フォルダのパス
THUMBNAIL_FOLDER = "/thumbnail"

# Sample文字が入っている等倍画像の保存先フォルダのパス
WITH_SAMPLE_TEXT_FOLDER = "/sample"

# Sample文字が入っていサムネイル用画像の保存先フォルダのパス
WITH_SAMPLE_THUMBNAIL_FOLDER = "/sample-thumbnail"

def get_first_image(subfolder_path):
    for root, dirs, files in os.walk(subfolder_path):
        for file in files:
            if file.lower().endswith(('.png')):
                return os.path.join(root, file).replace("\\", "/")
    return None

def get_subfolders(folder_path, is_sample=True):
    subfolders = []
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            subfolder_path = os.path.join(root, dir).replace("\\", "/")
            if is_sample:
                # サブフォルダの文字列にsample, sample-thumbnail, thumbnailが含まれた場合は除外
                if any(x in subfolder_path for x in [WITH_SAMPLE_TEXT_FOLDER, WITH_SAMPLE_THUMBNAIL_FOLDER, THUMBNAIL_FOLDER]):
                    continue
                first_image = get_first_image(subfolder_path + WITH_SAMPLE_THUMBNAIL_FOLDER)
            else:
                first_image = get_first_image(subfolder_path + THUMBNAIL_FOLDER)
            if first_image:
                subfolders.append((dir, first_image))
    return subfolders

@app.route('/')
def index():
    # URLのパラメータからis_sampleを取得
    is_sample_param = request.args.get('is_sample', 'true')
    
    # is_sampleパラメータが"false"の場合、Falseをセット
    if is_sample_param.lower() == 'false':
        is_sample = False
    else:
        is_sample = True

    # サブフォルダのリストを取得
    subfolder_images = get_subfolders(IMAGE_FOLDER, is_sample)
    return render_template('index.html', subfolder_images=subfolder_images, is_sample=is_sample)

@app.route('/subfolders/<subfolder_name>/')
def subfolder_images(subfolder_name):
    subfolder_path = os.path.join(IMAGE_FOLDER, subfolder_name).replace("\\", "/")
    thumbnail_folder = THUMBNAIL_FOLDER
    # URLのパラメータからis_sampleを取得
    is_sample_param = request.args.get('is_sample', 'true')
    
    # is_sampleパラメータが"false"の場合、Falseをセット
    if is_sample_param.lower() == 'false':
        is_sample = False
        subfolder_path = subfolder_path + THUMBNAIL_FOLDER
        thumbnail_folder = THUMBNAIL_FOLDER
    else:
        is_sample = True
        subfolder_path = subfolder_path + WITH_SAMPLE_THUMBNAIL_FOLDER
        thumbnail_folder = WITH_SAMPLE_THUMBNAIL_FOLDER

    print(subfolder_path)
    # サブフォルダ内の画像ファイルの一覧を取得
    image_files = [f.name for f in os.scandir(subfolder_path) if f.is_file() and f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    return render_template('subfolders.html', subfolder_name=subfolder_name, thumbnail_folder=thumbnail_folder, image_files=image_files, is_sample=is_sample)

@app.route('/images/<path:image_file>')
def get_image(image_file):
    # 原寸大の画像を表示
    return send_from_directory(IMAGE_FOLDER, image_file)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')