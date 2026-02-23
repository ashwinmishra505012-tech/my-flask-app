"""
Flask Application Entry Point
Main initialization file for the Medvika Pharmacy website application.

This file handles:
- Flask app creation and configuration
- Blueprint registration
- Template context processor setup
- Database initialization
"""

import os
import logging
from datetime import timedelta
from flask import Flask, session, redirect, url_for, flash, request, Response
from config import SECRET_KEY, DEBUG, DATABASE, UPLOAD_FOLDER_PHOTOS, UPLOAD_FOLDER_VIDEOS, PERMANENT_SESSION_LIFETIME, SESSION_REFRESH_EACH_REQUEST, DEFAULT_SETTINGS
from models import init_db, get_db_connection
from utils.helpers import get_social_links


# ===== APP INITIALIZATION =====

app = Flask(__name__)

# Configure Flask
app.secret_key = SECRET_KEY
app.debug = DEBUG
app.config['UPLOAD_FOLDER_PHOTOS'] = UPLOAD_FOLDER_PHOTOS
app.config['UPLOAD_FOLDER_VIDEOS'] = UPLOAD_FOLDER_VIDEOS
app.config['DATABASE'] = DATABASE

# Session Configuration - 15 minute timeout
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME
app.config['SESSION_REFRESH_EACH_REQUEST'] = SESSION_REFRESH_EACH_REQUEST

# ===== ACCESS LOGGING =====
# Use built-in logging to append request access entries to `access.log`.
# Format includes date/time (configured via basicConfig), log level and message.
logging.basicConfig(
    filename='access.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


@app.before_request
def log_request_info():
    """Log basic access info for each request: datetime, IP, method, path.
    Keep the message minimal and avoid logging form bodies or query data.
    """
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        # Log: prefix 'ACCESS' to make parsing easier
        logging.info('ACCESS %s %s %s', ip or '-', request.method, request.path)
    except Exception:
        # Swallow logging errors to avoid impacting requests
        pass

# Import and register blueprints
from routes import public_bp, admin_bp

app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)


# ===== TEMPLATE CONTEXT PROCESSORS =====

@app.context_processor
def inject_global_data():
    """
    Inject social media links and site settings into all templates.
    This makes the social_links and site_settings variables available in every template.
    """
    try:
        conn = get_db_connection()
        settings = conn.execute('SELECT * FROM settings WHERE id = 1').fetchone()
        conn.close()
        if settings is None:
            settings = DEFAULT_SETTINGS
    except Exception:
        settings = DEFAULT_SETTINGS
    
    return {
        'social_links': get_social_links(),
        'site_settings': settings
    }


# ===== GENERAL ROUTES =====

@app.route('/logout')
def logout():
    """Logout admin and clear session."""
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin.admin_login'))


@app.route('/favicon.ico')
def favicon():
    """Generate and serve favicon SVG."""
    favicon_svg = '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
        <defs>
            <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#3ecf8e;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#1e7f5c;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="200" height="200" fill="url(#bgGrad)" rx="40"/>
        <text x="100" y="105" font-family="'Poppins', Arial, sans-serif" font-size="80" font-weight="900" fill="white" text-anchor="middle" dominant-baseline="middle">M</text>
        <text x="100" y="160" font-family="'Poppins', Arial, sans-serif" font-size="28" font-weight="700" fill="white" text-anchor="middle" letter-spacing="1">Medvika</text>
    </svg>
    '''
    return Response(favicon_svg, mimetype='image/svg+xml')


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return "Internal server error", 500


# ===== MAIN ENTRY POINT =====

if __name__ == '__main__':
    # Create upload directories if they don't exist
    os.makedirs(UPLOAD_FOLDER_PHOTOS, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER_VIDEOS, exist_ok=True)
    
    # Initialize database
    if not os.path.exists(DATABASE):
        init_db()
    
    # Run the app
    app.run(debug=DEBUG)
