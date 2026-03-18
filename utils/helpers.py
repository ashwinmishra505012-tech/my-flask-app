"""
Helper functions and utilities for file handling and data processing.
Contains file validation, template context injection, and icon mappings.
"""

from config import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, PLATFORM_ICONS
from models import get_db_connection


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
