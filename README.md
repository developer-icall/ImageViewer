# 更新、起動方法

1. ソースコードがある階層(sources/ImageViewer)にて `git pull` を実行
2. トップ階層(本ファイルがある階層)にて以下を実行
    ```
    docker-compose build
    docker-compose down
    docker-compose up -d
    ```
