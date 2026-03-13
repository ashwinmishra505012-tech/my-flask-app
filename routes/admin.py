"""
Admin panel routes for content management.
Includes: login, dashboard, upload, manage, edit, delete, messages, map, style, links, settings.
"""

import os
import sqlite3
import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from routes import admin_bp
from models import get_db_connection
from utils import admin_login_required, verify_admin_credentials
from utils.helpers import allowed_file, get_platform_icon, validate_image_file, validate_video_file
from config import (
    UPLOAD_FOLDER_PHOTOS, UPLOAD_FOLDER_VIDEOS, 
    ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS,
    PLATFORM_ICONS, DEFAULT_SETTINGS, DEFAULT_MAP_SETTINGS, DEFAULT_STYLE_SETTINGS,
    RATELIMIT_STORAGE_URI, RATELIMIT_STRATEGY
)


# Rate limiter for admin routes
admin_limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=RATELIMIT_STORAGE_URI,
    strategy=RATELIMIT_STRATEGY
)


# ===== ADMIN LOGIN & LOGOUT =====

@admin_bp.route('', methods=['GET', 'POST'])
@admin_limiter.limit("5 per minute")  # Stricter limit for login attempts
def admin_login():
    """
    Admin login page.
    Authenticates admin credentials and creates session.
    """
    if 'admin_logged_in' in session:
        return redirect(url_for('admin.admin_dashboard'))
    
    error = None
    # default field-level messages and attempted password for GET renders
    username_error = None
    password_error = None
    wrong_password = None

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        username_error = None
        password_error = None
        wrong_password = None

        # Load stored admin credentials from settings
        try:
            conn = get_db_connection()
            row = conn.execute('SELECT admin_username, admin_password FROM settings WHERE id = 1').fetchone()
            conn.close()
        except Exception:
            row = None

        stored_user = row['admin_username'] if row and row['admin_username'] else 'admin'
        stored_hash = row['admin_password'] if row else None

        # Validate username first
        if username != stored_user:
            username_error = 'Invalid username'
            error = 'Invalid credentials'
        else:
            # Username correct — validate password
            try:
                if stored_hash:
                    if not check_password_hash(stored_hash, password):
                        password_error = 'Invalid password'
                        wrong_password = password
                        error = 'Invalid credentials'
                    else:
                        # success
                        try:
                            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                            if ip and ',' in ip:
                                ip = ip.split(',')[0].strip()
                            logging.info('ADMIN_LOGIN %s %s', ip or '-', username)
                        except Exception:
                            pass
                        session.permanent = True
                        session['admin_logged_in'] = True
                        return redirect(url_for('admin.admin_dashboard'))
                else:
                    # No password hash set - deny login and log security issue
                    logging.warning('ADMIN_LOGIN_ATTEMPT_NO_HASH %s', username)
                    password_error = 'Invalid password'
                    error = 'Invalid credentials'
            except Exception:
                error = 'Invalid credentials'
            # If we reach here due to an exception, do not reveal password; keep wrong_password as previously set
    
    return render_template('admin/login.html', error=error, wrong_password=wrong_password, username_error=username_error, password_error=password_error)


# ===== ADMIN DASHBOARD =====

@admin_bp.route('/dashboard')
@admin_login_required
def admin_dashboard():
    """
    Admin dashboard with summary statistics.
    Shows counts of photos, videos, messages and recent uploads.
    """
    conn = get_db_connection()
    try:
        total_photos = conn.execute(
            'SELECT COUNT(*) as c FROM admin_content WHERE media_type = "photo"'
        ).fetchone()['c']
        total_videos = conn.execute(
            'SELECT COUNT(*) as c FROM admin_content WHERE media_type = "video"'
        ).fetchone()['c']
        new_messages = conn.execute(
            'SELECT COUNT(*) as c FROM messages'
        ).fetchone()['c']
        recent_uploads = conn.execute(
            'SELECT * FROM admin_content ORDER BY created_at DESC LIMIT 6'
        ).fetchall()
    except Exception:
        # Fallback if tables don't exist yet
        total_photos = 0
        total_videos = 0
        new_messages = 0
        recent_uploads = []
    finally:
        conn.close()

    # Placeholder for visitor tracking (can be extended)
    visitors_today = '1,294'

    return render_template('admin/dashboard.html',
                           total_photos=total_photos,
                           total_videos=total_videos,
                           new_messages=new_messages,
                           recent_uploads=recent_uploads,
                           visitors_today=visitors_today)


# ===== ADMIN UPLOAD & MANAGEMENT =====

@admin_bp.route('/upload', methods=['GET', 'POST'])
@admin_login_required
def admin_upload():
    """
    Upload media (photos/videos) to gallery.
    Handles both GET (form display) and POST (file upload).
    """
    conn = get_db_connection()
    message = None
    message_type = 'success'
    
    if request.method == 'POST':
        media_type = request.form.get('media_type')
        file = request.files.get('file')
        title = request.form.get('title', '').strip()[:50]
        description = request.form.get('description', '').strip()[:50]
        
        # Validate form inputs
        if not (media_type and file and title and description):
            message = 'All fields are required.'
            message_type = 'error'
        elif media_type == 'photo' and validate_image_file(file):
            # Save photo
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER_PHOTOS, filename)
            file.save(save_path)
            db_path = save_path
            message = None
        elif media_type == 'video' and validate_video_file(file):
            # Save video
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER_VIDEOS, filename)
            file.save(save_path)
            db_path = save_path
            message = None
        else:
            message = 'Invalid file type or corrupted file.'
            message_type = 'error'
            db_path = None
        
        # Insert into database if file saved successfully
        if not message:
            now = datetime.now()
            conn.execute(
                'INSERT INTO admin_content (media_type, file_path, title, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (media_type, db_path, title, description, 'visible', now, now)
            )
            conn.commit()
            message = 'File uploaded successfully!'
            message_type = 'success'
    
    # Fetch all content for display
    content = conn.execute('SELECT * FROM admin_content ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin/upload.html', message=message, message_type=message_type, content=content)


@admin_bp.route('/manage')
@admin_login_required
def admin_manage():
    """Display all uploaded content for management."""
    conn = get_db_connection()
    content = conn.execute('SELECT * FROM admin_content ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/manage.html', content=content)


@admin_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_login_required
def admin_edit(item_id):
    """
    Edit content details (title, description, status, file).
    GET: Display edit form
    POST: Save changes to database
    """
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM admin_content WHERE id = ?', (item_id,)).fetchone()
    message = None
    message_type = 'success'
    
    if not item:
        conn.close()
        return redirect(url_for('admin.admin_manage'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()[:50]
        description = request.form.get('description', '').strip()[:50]
        status = request.form.get('status', 'visible')
        file = request.files.get('file')
        db_path = item['file_path']
        
        # Handle file replacement
        if file and file.filename:
            try:
                if os.path.exists(item['file_path']):
                    os.remove(item['file_path'])
            except Exception:
                pass
            
            # Save new file
            if item['media_type'] == 'photo' and is_allowed_image(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER_PHOTOS, filename)
                file.save(save_path)
                db_path = save_path
            elif item['media_type'] == 'video' and is_allowed_video(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER_VIDEOS, filename)
                file.save(save_path)
                db_path = save_path
            else:
                message = 'Invalid file type.'
                message_type = 'error'
        
        # Update database if no errors
        if not message:
            now = datetime.now()
            conn.execute(
                'UPDATE admin_content SET title=?, description=?, status=?, file_path=?, updated_at=? WHERE id=?',
                (title, description, status, db_path, now, item_id)
            )
            conn.commit()
            message = 'Content updated successfully!'
            message_type = 'success'
            item = conn.execute('SELECT * FROM admin_content WHERE id = ?', (item_id,)).fetchone()
    
    conn.close()
    return render_template('admin/edit.html', item=item, message=message, message_type=message_type)


@admin_bp.route('/update/<int:item_id>', methods=['POST'])
@admin_login_required
def admin_update(item_id):
    """
    AJAX endpoint to update content inline.
    Accepts JSON with title and/or description.
    """
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM admin_content WHERE id = ?', (item_id,)).fetchone()
    
    if not item:
        conn.close()
        return jsonify({'success': False, 'error': 'Item not found'})
    
    data = request.get_json()
    try:
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({'success': False, 'error': 'Title cannot be empty'})
            conn.execute('UPDATE admin_content SET title = ? WHERE id = ?', (title, item_id))
        
        if 'description' in data:
            description = data['description'].strip()
            if not description:
                return jsonify({'success': False, 'error': 'Description cannot be empty'})
            conn.execute('UPDATE admin_content SET description = ? WHERE id = ?', (description, item_id))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)})


@admin_bp.route('/delete/<int:item_id>', methods=['POST'])
@admin_login_required
def admin_delete(item_id):
    """AJAX endpoint to delete content and its file."""
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM admin_content WHERE id = ?', (item_id,)).fetchone()
    
    if not item:
        conn.close()
        return jsonify({'success': False, 'error': 'Item not found'})
    
    # Delete physical file
    try:
        if os.path.exists(item['file_path']):
            os.remove(item['file_path'])
    except Exception:
        pass
    
    # Delete database record
    conn.execute('DELETE FROM admin_content WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


# ===== ADMIN MESSAGES =====

@admin_bp.route('/messages')
@admin_login_required
def admin_messages():
    """Display all contact form messages."""
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY sent_time DESC').fetchall()
    conn.close()
    return render_template('admin/messages.html', messages=messages)


@admin_bp.route('/message/count')
@admin_login_required
def admin_message_count():
    """AJAX endpoint to get message count."""
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
    conn.close()
    return jsonify({'count': count})


@admin_bp.route('/message/delete/<int:msg_id>', methods=['POST'])
@admin_login_required
def admin_delete_message(msg_id):
    """AJAX endpoint to delete a message."""
    conn = get_db_connection()
    conn.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ===== ADMIN MAP SETTINGS =====

@admin_bp.route('/map')
@admin_login_required
def admin_map():
    """Display map settings editor."""
    conn = get_db_connection()
    map_data = conn.execute('SELECT * FROM map_settings WHERE id = 1').fetchone()
    conn.close()
    
    if map_data is None:
        map_data = DEFAULT_MAP_SETTINGS
    
    return render_template('admin/map.html', map_data=map_data)


@admin_bp.route('/map/update', methods=['POST'])
@admin_login_required
def update_map():
    """Update map settings."""
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    address = request.form.get('address')
    embed_url = request.form.get('embed_url')
    
    conn = get_db_connection()
    
    # Check if record exists
    existing = conn.execute('SELECT id FROM map_settings WHERE id = 1').fetchone()
    
    if existing:
        conn.execute(
            'UPDATE map_settings SET latitude = ?, longitude = ?, address = ?, embed_url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1',
            (latitude, longitude, address, embed_url)
        )
    else:
        conn.execute(
            'INSERT INTO map_settings (id, latitude, longitude, address, embed_url, updated_at) VALUES (1, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
            (latitude, longitude, address, embed_url)
        )
    
    conn.commit()
    conn.close()
    
    flash('Map settings updated successfully!', 'success')
    return redirect(url_for('admin.admin_map'))


# ===== ADMIN STYLE SETTINGS =====

@admin_bp.route('/style')
@admin_login_required
def admin_style():
    """Display style settings editor."""
    conn = get_db_connection()
    style_data = conn.execute('SELECT * FROM style_settings WHERE id = 1').fetchone()
    conn.close()
    
    if style_data is None:
        style_data = DEFAULT_STYLE_SETTINGS
    
    return render_template('admin/style.html', settings=style_data, message='')


@admin_bp.route('/style/save', methods=['POST'])
@admin_login_required
def save_style():
    """Save style settings."""
    font_family = request.form.get('font_family', 'Inter, sans-serif')
    font_color = request.form.get('font_color', '#333333')
    
    conn = get_db_connection()
    
    # Check if record exists
    existing = conn.execute('SELECT id FROM style_settings WHERE id = 1').fetchone()
    
    if existing:
        conn.execute(
            'UPDATE style_settings SET font_family = ?, font_color = ? WHERE id = 1',
            (font_family, font_color)
        )
    else:
        conn.execute(
            'INSERT INTO style_settings (id, font_family, font_color) VALUES (1, ?, ?)',
            (font_family, font_color)
        )
    
    conn.commit()
    conn.close()
    
    flash('Style settings updated successfully!', 'success')
    return redirect(url_for('admin.admin_style'))


# ===== ADMIN SOCIAL LINKS =====

@admin_bp.route('/link')
@admin_login_required
def admin_link():
    """Display social links management page."""
    conn = get_db_connection()
    links = conn.execute('SELECT * FROM social_links ORDER BY id').fetchall()
    conn.close()
    return render_template('admin/link.html', links=links)


@admin_bp.route('/link/add', methods=['POST'])
@admin_login_required
def admin_link_add():
    """AJAX endpoint to add a social link."""
    platform = request.form.get('platform', '').strip()
    link_url = request.form.get('link_url', '').strip()
    
    if not platform or not link_url:
        return jsonify({'success': False, 'error': 'Platform and URL required'}), 400
    
    # Get icon automatically based on platform
    icon = get_platform_icon(platform)
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO social_links (platform, icon, link_url) VALUES (?, ?, ?)',
                    (platform, icon, link_url))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Platform already exists'}), 400


@admin_bp.route('/link/update/<int:link_id>', methods=['POST'])
@admin_login_required
def admin_link_update(link_id):
    """AJAX endpoint to update a social link."""
    platform = request.form.get('platform', '').strip()
    link_url = request.form.get('link_url', '').strip()
    
    if not platform or not link_url:
        return jsonify({'success': False, 'error': 'Platform and URL required'}), 400
    
    conn = get_db_connection()
    try:
        conn.execute('UPDATE social_links SET platform = ?, link_url = ? WHERE id = ?',
                    (platform, link_url, link_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Platform already exists'}), 400


@admin_bp.route('/link/delete/<int:link_id>', methods=['POST'])
@admin_login_required
def admin_link_delete(link_id):
    """AJAX endpoint to delete a social link."""
    conn = get_db_connection()
    conn.execute('DELETE FROM social_links WHERE id = ?', (link_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ===== ADMIN GENERAL SETTINGS =====

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_login_required
def admin_settings():
    """
    Admin settings page for website configuration.
    GET: Display settings form
    POST: Update website and admin settings
    """
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Extract website settings
        website_name = request.form.get('website_name', 'Medvika Pharmacy')
        website_description = request.form.get('website_description', '')
        contact_email = request.form.get('contact_email', '')
        contact_phone = request.form.get('contact_phone', '')
        contact_address = request.form.get('contact_address', '')
        business_hours = request.form.get('business_hours', '')
        footer_text = request.form.get('footer_text', '')
        footer_description = request.form.get('footer_description', '')
        meta_description = request.form.get('meta_description', '')
        meta_keywords = request.form.get('meta_keywords', '')
        enable_gallery = 1 if request.form.get('enable_gallery') else 0
        enable_contact = 1 if request.form.get('enable_contact') else 0
        enable_reviews = 1 if request.form.get('enable_reviews') else 0
        
        # Extract admin credentials
        admin_username = request.form.get('admin_username', '').strip()
        admin_old_password = request.form.get('admin_old_password', '')
        admin_password = request.form.get('admin_password', '')
        admin_password_confirm = request.form.get('admin_password_confirm', '')
        hashed = None
        
        # Validate and hash new password if provided
        if admin_password:
            row = conn.execute('SELECT admin_password, admin_username FROM settings WHERE id = 1').fetchone()
            stored_hash = row['admin_password'] if row else None
            
            # Require old password
            if not admin_old_password:
                conn.close()
                flash('Current password is required to change admin password.', 'danger')
                return redirect(url_for('admin.admin_settings'))
            
            # Verify old password
            if stored_hash:
                try:
                    if not check_password_hash(stored_hash, admin_old_password):
                        conn.close()
                        flash('Current password is incorrect.', 'danger')
                        return redirect(url_for('admin.admin_settings'))
                except Exception:
                    conn.close()
                    flash('Error verifying current password.', 'danger')
                    return redirect(url_for('admin.admin_settings'))
            
            # Verify confirmation matches
            if admin_password != admin_password_confirm:
                conn.close()
                flash('New password and confirmation do not match.', 'danger')
                return redirect(url_for('admin.admin_settings'))
            
            # Hash new password
            hashed = generate_password_hash(admin_password)
        
        # Update database
        existing = conn.execute('SELECT id FROM settings WHERE id = 1').fetchone()
        
        if existing:
            if hashed:
                conn.execute('''UPDATE settings SET 
                    website_name=?, website_description=?, contact_email=?, contact_phone=?,
                    contact_address=?, business_hours=?, footer_text=?, footer_description=?,
                    meta_description=?, meta_keywords=?, enable_gallery=?, enable_contact=?, enable_reviews=?, admin_username=?, admin_password=?
                    WHERE id = 1''',
                    (website_name, website_description, contact_email, contact_phone, contact_address,
                     business_hours, footer_text, footer_description, meta_description, meta_keywords,
                     enable_gallery, enable_contact, enable_reviews, admin_username or None, hashed))
            else:
                conn.execute('''UPDATE settings SET 
                    website_name=?, website_description=?, contact_email=?, contact_phone=?,
                    contact_address=?, business_hours=?, footer_text=?, footer_description=?,
                    meta_description=?, meta_keywords=?, enable_gallery=?, enable_contact=?, enable_reviews=?, admin_username=?
                    WHERE id = 1''',
                    (website_name, website_description, contact_email, contact_phone, contact_address,
                     business_hours, footer_text, footer_description, meta_description, meta_keywords,
                     enable_gallery, enable_contact, enable_reviews, admin_username or None))
        else:
            conn.execute('''INSERT INTO settings 
                (id, website_name, website_description, contact_email, contact_phone, contact_address,
                 business_hours, footer_text, footer_description, meta_description, meta_keywords,
                 enable_gallery, enable_contact, enable_reviews, admin_username, admin_password)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (website_name, website_description, contact_email, contact_phone, contact_address,
                 business_hours, footer_text, footer_description, meta_description, meta_keywords,
                 enable_gallery, enable_contact, enable_reviews, admin_username or 'admin', 
                 hashed or generate_password_hash('password')))
        
        conn.commit()
        conn.close()
        # If password was changed, require re-login for security
        if hashed:
            session.pop('admin_logged_in', None)
            flash('Password changed — please log in again with the new password.', 'success')
            return redirect(url_for('admin.admin_login'))

        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.admin_settings'))
    
    # Fetch current settings
    settings = conn.execute('SELECT * FROM settings WHERE id = 1').fetchone()
    conn.close()
    
    if settings is None:
        settings = DEFAULT_SETTINGS
    
    return render_template('admin/settings.html', settings=settings)


# ===== ADMIN DOCTOR MANAGEMENT =====

@admin_bp.route('/doctors', methods=['GET', 'POST'])
@admin_login_required
def admin_doctors():
    """
    Doctor management page - add, edit, delete doctors for team section.
    """
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM doctors ORDER BY display_order, created_at').fetchall()
    conn.close()
    
    return render_template('admin/doctors.html', doctors=doctors)


@admin_bp.route('/doctor/add', methods=['POST'])
@admin_login_required
def admin_doctor_add():
    """Add a new doctor."""
    try:
        name = request.form.get('name', '').strip()
        qualification = request.form.get('qualification', '').strip()
        designation = request.form.get('designation', '').strip()
        status = request.form.get('status', 'visible')
        
        if not name:
            return jsonify({'success': False, 'error': 'Doctor name is required'}), 400
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and is_allowed_image(file.filename):
                filename = secure_filename(f"doctor_{name.replace(' ', '_')}_{datetime.now().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}")
                os.makedirs(UPLOAD_FOLDER_PHOTOS, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER_PHOTOS, filename))
                image_path = f"static/uploads/photos/{filename}"
        
        if not image_path:
            return jsonify({'success': False, 'error': 'Doctor photo is required'}), 400
        
        conn = get_db_connection()
        conn.execute('''INSERT INTO doctors (name, qualification, designation, image_path, status, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (name, qualification or 'Professional', designation or None, image_path, status, datetime.now(), datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/doctor/edit/<int:doctor_id>', methods=['POST'])
@admin_login_required
def admin_doctor_edit(doctor_id):
    """Edit an existing doctor."""
    try:
        name = request.form.get('name', '').strip()
        qualification = request.form.get('qualification', '').strip()
        designation = request.form.get('designation', '').strip()
        status = request.form.get('status', 'visible')
        
        if not name:
            return jsonify({'success': False, 'error': 'Doctor name is required'}), 400
        
        conn = get_db_connection()
        doctor = conn.execute('SELECT image_path FROM doctors WHERE id = ?', (doctor_id,)).fetchone()
        
        image_path = doctor['image_path'] if doctor else None
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and is_allowed_image(file.filename):
                # Delete old image if exists
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass
                
                filename = secure_filename(f"doctor_{name.replace(' ', '_')}_{datetime.now().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}")
                os.makedirs(UPLOAD_FOLDER_PHOTOS, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER_PHOTOS, filename))
                image_path = f"static/uploads/photos/{filename}"
        
        conn.execute('''UPDATE doctors SET name = ?, qualification = ?, designation = ?, image_path = ?, status = ?, updated_at = ?
                       WHERE id = ?''',
                    (name, qualification or 'Professional', designation or None, image_path, status, datetime.now(), doctor_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/doctor/delete/<int:doctor_id>', methods=['POST'])
@admin_login_required
def admin_doctor_delete(doctor_id):
    """Delete a doctor."""
    try:
        conn = get_db_connection()
        doctor = conn.execute('SELECT image_path FROM doctors WHERE id = ?', (doctor_id,)).fetchone()
        
        if doctor and doctor['image_path'] and os.path.exists(doctor['image_path']):
            try:
                os.remove(doctor['image_path'])
            except:
                pass
        
        conn.execute('DELETE FROM doctors WHERE id = ?', (doctor_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/doctors-count', methods=['GET'])
@admin_login_required
def admin_doctors_count():
    """Get count of doctors for display."""
    try:
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) as total FROM doctors WHERE status = ?', ('visible',)).fetchone()
        conn.close()
        return jsonify({'count': count['total'] or 0})
    except Exception as e:
        return jsonify({'count': 0, 'error': str(e)})


@admin_bp.route('/get-all-doctors', methods=['GET'])
@admin_login_required
def admin_get_all_doctors():
    """Get all doctors for display in upload page."""
    try:
        conn = get_db_connection()
        doctors = conn.execute(
            'SELECT id, name, qualification, designation, image_path, status FROM doctors ORDER BY display_order, created_at DESC'
        ).fetchall()
        conn.close()
        return jsonify([dict(doc) for doc in doctors])
    except Exception as e:
        return jsonify({'error': str(e)})
