"""
Helper functions and utilities for file handling and data processing.
Contains file validation, template context injection, icon mappings, and caching.
"""

import time
from config import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, PLATFORM_ICONS
from models import get_db_connection


# ===== SIMPLE IN-MEMORY CACHE =====

# Global cache storage: {key: {'data': value, 'timestamp': time}}
_cache = {}
CACHE_TIMEOUT = 10  # seconds (configurable)


def cache_get(key):
    """
    Get cached data if not expired. Returns None if expired or not found.
    Usage: data = cache_get('dashboard_stats')
    """
    if key not in _cache:
        return None
    
    cached_item = _cache[key]
    age = time.time() - cached_item['timestamp']
    
    if age > CACHE_TIMEOUT:
        # Cache expired, remove it
        del _cache[key]
        return None
    
    return cached_item['data']


def cache_set(key, value):
    """
    Store data in cache with current timestamp.
    Usage: cache_set('dashboard_stats', {'total_photos': 42})
    """
    _cache[key] = {
        'data': value,
        'timestamp': time.time()
    }


def cache_clear(key=None):
    """
    Clear specific cache key or all cache if key is None.
    Usage: cache_clear('dashboard_stats')  # clear one
           cache_clear()                     # clear all
    """
    global _cache
    if key is None:
        _cache = {}
    elif key in _cache:
        del _cache[key]


# ===== FILE VALIDATION =====

def allowed_file(filename, allowed_exts):
    """
    Check if a file has an allowed extension.
    Returns True if file is acceptable, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


def is_allowed_image(filename):
    """Check if filename is an allowed image file."""
    return allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS)


def is_allowed_video(filename):
    """Check if filename is an allowed video file."""
    return allowed_file(filename, ALLOWED_VIDEO_EXTENSIONS)


def get_platform_icon(platform):
    """
    Get Font Awesome icon class for a given social media platform.
    Returns icon class or default globe icon if platform not found.
    """
    return PLATFORM_ICONS.get(platform, 'fab fa-globe')


def get_social_links():
    """
    Fetch all social media links from database.
    Used as template context processor to inject links into all templates.
    Returns list of social links or empty list if error occurs.
    """
    try:
        conn = get_db_connection()
        links = conn.execute('SELECT * FROM social_links ORDER BY id').fetchall()
        conn.close()
        return links
    except Exception:
        return []
