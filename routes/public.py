"""
Public routes for the front-end website.
Includes: home, about, contact, gallery pages.
"""

from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
from routes import public_bp
from models import get_db_connection
from config import DEFAULT_MAP_SETTINGS
from models import get_db_connection
from config import DEFAULT_SETTINGS


@public_bp.route('/')
def home():
    """Home page route."""
    # Load site settings for template
    conn = get_db_connection()
    settings = conn.execute('SELECT * FROM settings WHERE id = 1').fetchone()
    conn.close()
    if settings is None:
        settings = DEFAULT_SETTINGS
    return render_template('home.html', settings=settings)


@public_bp.route('/about')
def about():
    """About page route."""
    conn = get_db_connection()
    settings = conn.execute('SELECT * FROM settings WHERE id = 1').fetchone()
    doctors = conn.execute('SELECT * FROM doctors WHERE status = ? ORDER BY display_order, created_at', ('visible',)).fetchall()
    conn.close()
    if settings is None:
        settings = DEFAULT_SETTINGS
    return render_template('about.html', settings=settings, doctors=doctors)


@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Contact page route.
    GET: Display contact form and map
    POST: Save contact message to database
    """
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            mobile = request.form.get('mobile', '').strip()
            message = request.form.get('message', '').strip()
            
            # Validate required fields
            if not all([name, email, message]):
                flash('Please fill in all required fields (Name, Email, Message)', 'danger')
                return redirect(url_for('public.contact'))
            
            # Save message to database
            conn = get_db_connection()
            conn.execute('INSERT INTO messages (name, email, mobile, message, sent_time) VALUES (?, ?, ?, ?, ?)',
                         (name, email, mobile, message, datetime.now()))
            conn.commit()
            conn.close()
            
            flash('Message sent successfully! We will get back to you soon.', 'success')
            return redirect(url_for('public.contact'))
        except Exception as e:
            flash(f'Error sending message: {str(e)}', 'danger')
            return redirect(url_for('public.contact'))
    
    # Get map data and site settings from database
    conn = get_db_connection()
    map_data = conn.execute('SELECT * FROM map_settings WHERE id = 1').fetchone()
    settings = conn.execute('SELECT * FROM settings WHERE id = 1').fetchone()
    conn.close()
    
    # Use default map data if not set in database
    if map_data is None:
        map_data = DEFAULT_MAP_SETTINGS
    
    if settings is None:
        settings = DEFAULT_SETTINGS

    return render_template('contact.html', map_data=map_data, settings=settings)


@public_bp.route('/gallery')
def gallery():
    """
    Public gallery page showing visible photos and videos.
    Only displays content with status='visible'.
    """
    conn = get_db_connection()
    photos = conn.execute(
        'SELECT * FROM admin_content WHERE media_type = "photo" AND status = "visible" ORDER BY created_at DESC'
    ).fetchall()
    videos = conn.execute(
        'SELECT * FROM admin_content WHERE media_type = "video" AND status = "visible" ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    
    return render_template('gallery.html', photos=photos, videos=videos)
