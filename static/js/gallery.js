// gallery.js - toggles between photos and videos in the gallery

document.addEventListener('DOMContentLoaded', function() {
    const btnPhotos = document.getElementById('show-photos');
    const btnVideos = document.getElementById('show-videos');
    const photosGrid = document.getElementById('gallery-photos');
    const videosGrid = document.getElementById('gallery-videos');

    if (btnPhotos && btnVideos && photosGrid && videosGrid) {
        btnPhotos.addEventListener('click', function() {
            btnPhotos.classList.add('active');
            btnVideos.classList.remove('active');
            photosGrid.style.display = '';
            videosGrid.style.display = 'none';
        });
        btnVideos.addEventListener('click', function() {
            btnVideos.classList.add('active');
            btnPhotos.classList.remove('active');
            videosGrid.style.display = '';
            photosGrid.style.display = 'none';
        });
    }
});
