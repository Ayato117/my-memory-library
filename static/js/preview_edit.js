document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("diary_image");
    const imagePreviewContainer = document.getElementById("image_preview_container");
    const videoPreviewContainer = document.getElementById("video_preview_container");
    const imagePreview = document.getElementById("image_preview");
    const videoPreview = document.getElementById("video_preview");
    const deleteButton = document.getElementById("delete_media_button");
    const existingImageUrl = document.getElementById("existing_imageurl");

    function resetPreview() {
        imagePreviewContainer.style.display = "none";
        videoPreviewContainer.style.display = "none";
        imagePreview.src = "#";
        videoPreview.src = "";
        deleteButton.style.display = "none";
    }

    // 初期表示時に既存メディアを表示
    if (existingImageUrl && existingImageUrl.value) {
        if (existingImageUrl.value.match(/\.(jpeg|jpg|png|gif)$/)) {
            imagePreview.src = existingImageUrl.value;
            imagePreviewContainer.style.display = "block";
        } else if (existingImageUrl.value.match(/\.(mp4|webm|ogg)$/)) {
            videoPreview.src = existingImageUrl.value;
            videoPreviewContainer.style.display = "block";
        }
        deleteButton.style.display = "inline";
    }

    fileInput.addEventListener("change", function () {
        const file = fileInput.files[0];
        resetPreview();
        if (!file) return;

        const reader = new FileReader();
        reader.onloadend = function () {
            if (file.type.startsWith("image/")) {
                imagePreview.src = reader.result;
                imagePreviewContainer.style.display = "block";
            } else if (file.type.startsWith("video/")) {
                videoPreview.src = reader.result;
                videoPreviewContainer.style.display = "block";
            }
            deleteButton.style.display = "inline";
        };
        reader.readAsDataURL(file);
    });

    deleteButton.addEventListener("click", function () {
        fileInput.value = "";
        existingImageUrl.value = "";
        resetPreview();
    });
});
