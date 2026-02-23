// home.js - JS for home page

// Switch image on screen resize
function updatePartnerImage() {
    const img = document.querySelector('.why-partner-img');
    if (!img) return;
    
    const mobileSrc = img.getAttribute('data-mobile-src');
    const desktopSrc = img.src;
    
    if (window.innerWidth <= 900) {
        if (mobileSrc && img.src !== mobileSrc) {
            img.src = mobileSrc;
        }
    } else {
        if (img.src !== desktopSrc && !img.src.includes('pointdr')) {
            img.src = desktopSrc;
        }
    }
}

// Run on load and resize
window.addEventListener('load', updatePartnerImage);
window.addEventListener('resize', updatePartnerImage);
updatePartnerImage();