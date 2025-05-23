仕様追加があるので実装お願いします

# 今回追加する仕様

1. 表示する画像を選ぶオプションでユーザーが選択する大項目(style, 画像テイスト), 中項目(category, カテゴリ), 小項目(subcategory, 画像タイプ) それぞれについて、表示位置の並び替えおよび表示 or 非表示の制御ができるようにする
    - それぞれの表示順を設定ファイルで指定できるようにする
    - それぞれの表示 or 非表示を指定できるようにする
    - 選択された大項目および中項目に対する小項目がすべて非表示になっていたら「画像タイプ」の選択部分を非表示にする
2. サイトトップにアクセスした場合、大項目で表示順1番、中項目で表示順1番、中項目で表示順1番のページへリダイレクトする
3. 大項目をユーザーが選択した場合、中項目で表示順1番のページへリダイレクトする
4. 中項目をユーザーが選択した場合、小項目で表示順1番のページへリダイレクトする

# 以前実装した仕様
- 画像タイプを指定するオプションの表示について以下仕様を変更
    - 大項目として以下の2つを用意
        - リアルテイスト画像
        - ゲーム、イラスト風画像
    - 各大項目の中には以下の中・小項目を用意
        - リアルテイスト画像
            - 女性
                - 通常画像
                - 透明背景画像
                - セルフィー画像
            - 男性
                - 通常画像
                - 透明背景画像
                - セルフィー画像
            - 動物
                - 犬
                - 猫
                - 鳥
                - 魚
                - その他
        - ゲーム、イラスト風画像
            - 女性
                - 通常画像
                - 透明背景画像
                - セルフィー画像
            - 男性
                - 通常画像
                - 透明背景画像
                - セルフィー画像
            - 動物
                - 犬
                - 猫
                - 鳥
                - 魚
                - その他
            - 背景
                - 自然
                - 都市
                - 海
                - 空
                - その他
            - RPGアイコン
                - 武器・防具
                - モンスター
                - その他
            - 乗り物
                - 車
                - 船
                - 飛行機
                - その他
            - その他
- 大項目を選択すると、その大項目に中項目が表示される
- 中項目を選択すると、その中項目に小項目が表示される
- 小項目または選択すると、その項目の画像が表示される
- 小項目がない中項目を選択すると、その中項目の画像が表示される
- 大項目と中項目および小項目はパラメータではなく URL で判別できるようにする
- 既存のURLの階層ではなく、新たにURLの階層を作成する
    - 適した命名規則を考える
- ルート階層にアクセスした場合 ./realistic/female/nomarl にアクセスするようにする

# 注意事項

- 既存の templates フォルダ以下のファイルの仕様、デザインを必ず踏襲する
- できるだけ新しいテンプレートファイルは作成しない。本当に必要なら作成する

# 関連ファイル
@app.py @index.html @images.html @subfolders.html

---
以下のステップで進みたいですが、各ステップ毎に動作確認をするためのテストコードも合わせて作成し、テストをしつつ実装を進めてください

1. 追加する仕様1の実装のために、それぞれの表示順と表示 or 非表示を設定するための JSON ファイルを作成
2. ステップ1で作成した設定ファイルに沿って、それぞれの表示順を制御できるようにする
3. ステップ1で作成した設定ファイルに沿って、それぞれの表示 or 非表示を制御できるようにする
4. 選択された大項目および中項目に対する小項目がすべて非表示になっていたら「画像タイプ」の選択部分を非表示にする処理を実装
5. 仕様2～4を実装する。

それではステップ1からお願いします
