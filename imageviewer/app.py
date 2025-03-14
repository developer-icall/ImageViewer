import os
import re
import json
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
    g.prompt_separator = " / "  # プロンプトの区切り文字

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
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_path = os.path.join(root, file).replace("\\", "/")

                # フォルダ名を取得（例：20231124-17-1409855962）
                folder_name = os.path.basename(os.path.dirname(os.path.dirname(image_path)))

                # ベースフォルダを判定（brav, rpgicon, background）
                if RPGICON_FOLDER in subfolder_path:
                    base_folder = 'RPGIcon'
                elif BACKGROUND_FOLDER in subfolder_path:
                    base_folder = 'background'
                else:
                    base_folder = 'brav'

                # 画像のURLパスを構築
                return f"/images/{folder_name}/thumbnail/{file}"
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
            if not image_type.is_background and not image_type.is_rpgicon:
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

# JSONを基に、プロンプト情報を生成
def create_prompt(json_file, properties):
    separator = g.prompt_separator
    data = json.load(json_file) # jsonファイルを読み込む
    result = []
    for property in properties:
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

    # サブフォルダ内のjsonファイル（画像生成時のプロンプト）の内容を取得
    prompts = []
    for f in sorted(os.scandir(subfolder_path), key=lambda x: x.name.lower()):
        if f.is_file() and f.name.lower().endswith(('.json')):
            with open(f.path, 'r', encoding='utf-8') as json_file:
                prompt = create_prompt(json_file, ["Place", "pose", "Hair Color", "Hair Type", "Cloth", "Accesarry", "age", "Face", "Women Type"])
                if prompt:
                    prompts.append(prompt)

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
                         is_rpgicon=is_rpgicon,
                         prompts=prompts)

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

    # まず、bravフォルダで探す
    possible_paths = [
        f"sync_images/brav/{folder_name}{subfolder_name}/{image_path}",
        f"sync_images/RPGIcon/{folder_name}{subfolder_name}/{image_path}",
        f"sync_images/background/{folder_name}{subfolder_name}/{image_path}"
    ]

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

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')