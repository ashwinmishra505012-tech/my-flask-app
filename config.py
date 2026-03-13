"""
Configuration file for the Flask application.
Contains all environment variables, file paths, and constants.
"""

import os
from datetime import timedelta

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE_THIS_IN_PRODUCTION_TO_A_STRONG_RANDOM_KEY'
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'  # Default to False for security

# Session Configuration (15-minute timeout)
PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
SESSION_REFRESH_EACH_REQUEST = True  # Reset timer on each request
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'  # Set to True in production with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Database Configuration
DATABASE = os.path.join('instance', 'site.db')

# Upload Folder Configuration
UPLOAD_FOLDER_PHOTOS = 'static/uploads/photos/'
UPLOAD_FOLDER_VIDEOS = 'static/uploads/videos/'

# File Upload Security
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}

# Rate Limiting
RATELIMIT_STORAGE_URI = "memory://"  # Use Redis in production
RATELIMIT_DEFAULT = "200 per day;50 per hour"
RATELIMIT_STRATEGY = "fixed-window"

# Platform to Icon Mapping (Font Awesome)
PLATFORM_ICONS = {
    'Facebook': 'fab fa-facebook-f',
    'Instagram': 'fab fa-instagram',
    'Twitter': 'fab fa-twitter',
    'LinkedIn': 'fab fa-linkedin-in',
    'YouTube': 'fab fa-youtube',
    'TikTok': 'fab fa-tiktok',
    'Pinterest': 'fab fa-pinterest-p',
    'Snapchat': 'fab fa-snapchat-ghost',
    'WhatsApp': 'fab fa-whatsapp',
    'Telegram': 'fab fa-telegram',
}

# Default Settings
DEFAULT_SETTINGS = {
    'website_name': 'Medvika Pharmacy',
    'website_description': 'Trusted pharmacy delivering quality medicines with care',
    'contact_email': 'support@medvika.com',
    'contact_phone': '+91 9026805902',
    'contact_address': 'Delhi, India',
    'business_hours': 'Mon-Sun: 9:00 AM - 9:00 PM',
    'footer_text': 'Medvika Pharmacy - Your Trusted Healthcare Partner',
    'footer_description': 'Quality medicines delivered with care and responsibility',
    'meta_description': 'Online pharmacy delivering medicines',
    'meta_keywords': 'pharmacy, medicines, health',
    'enable_gallery': 1,
    'enable_contact': 1,
    'enable_reviews': 1
}

# Default Map Settings
DEFAULT_MAP_SETTINGS = {
    'latitude': 28.404497,
    'longitude': 77.203501,
    'address': 'Delhi, India',
    'embed_url': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3887.3045159289506!2d77.20350961490706!3d28.404497892399254!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390ce62c7c8f1111%3A0x8f8f8f8f8f8f8f8f!2sDelhi!5e0!3m2!1sen!2sin!4v1706867000000'
}

# Default Style Settings
DEFAULT_STYLE_SETTINGS = {
    'font_family': 'Inter, sans-serif',
    'font_color': '#333333'
}
