function previewMedia() {
    const file = document.getElementById('diary_image').files[0];
    const imagePreview = document.getElementById('image_preview');
    const videoPreview = document.getElementById('video_preview');
    const imagePreviewContainer = document.getElementById('image_preview_container');
    const videoPreviewContainer = document.getElementById('video_preview_container');
    const deleteButton = document.getElementById('delete_media_button');

    // プレビューと削除ボタンの初期状態を非表示にする
    imagePreviewContainer.style.display = 'none';
    videoPreviewContainer.style.display = 'none';
    deleteButton.style.display = 'none';

    if (!file) {
        return;
    }

    const fileType = file.type;
    const reader = new FileReader();

    reader.onloadend = function () {
        if (fileType.startsWith('image/')) {
            imagePreview.src = reader.result;
            imagePreviewContainer.style.display = 'block'; // 画像プレビューを表示
            videoPreviewContainer.style.display = 'none'; // 動画プレビューを非表示
            deleteButton.style.display = 'block'; // 削除ボタンを表示
        } else if (fileType.startsWith('video/')) {
            videoPreview.src = reader.result;
            videoPreviewContainer.style.display = 'block'; // 動画プレビューを表示
            imagePreviewContainer.style.display = 'none'; // 画像プレビューを非表示
            deleteButton.style.display = 'block'; // 削除ボタンを表示
        }
    };

    reader.readAsDataURL(file);
}

// メディア（画像または動画）の削除処理
function deleteMedia() {
    const fileInput = document.getElementById('diary_image');
    const deleteButton = document.getElementById('delete_media_button');
    const imagePreviewContainer = document.getElementById('image_preview_container');
    const videoPreviewContainer = document.getElementById('video_preview_container');
    
    fileInput.value = ''; // ファイル入力をリセット
    deleteButton.style.display = 'none'; // 削除ボタンを非表示
    imagePreviewContainer.style.display = 'none'; // 画像プレビューを非表示
    videoPreviewContainer.style.display = 'none'; // 動画プレビューを非表示
}
