function copyToClipboard(textToCopy) {

    // テキストエリアを動的に作成
    var textArea = document.createElement("textarea");
    textArea.value = textToCopy;

    // スタイルを設定して画面に表示されないようにする
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        // テキストをクリップボードにコピー
        var successful = document.execCommand('copy');
        var msg = successful ? 'successful' : 'unsuccessful';
        console.log('Copying text command was ' + msg);
    } catch (err) {
        console.log('Oops, unable to copy');
    }

    // テキストエリアを削除
    document.body.removeChild(textArea);
}
