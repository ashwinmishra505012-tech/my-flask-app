"""
Authentication utilities for admin panel.
Handles session management, login requirements, and password verification.
"""

from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from models import get_db_connection


def admin_login_required(f):
    """
    Decorator to protect admin routes.
    Redirects to login page if user is not authenticated.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated


def verify_admin_credentials(username, password):
    """
    Verify admin login credentials against database.
    Returns True if credentials are valid, False otherwise.
    """
    conn = get_db_connection()
    try:
        row = conn.execute('SELECT admin_username, admin_password FROM settings WHERE id = 1').fetchone()
    except Exception:
        row = None
    finally:
        conn.close()

    if row:
        stored_user = row['admin_username'] if row['admin_username'] else 'admin'
        stored_hash = row['admin_password']
        
        if stored_hash:
            try:
                ok = username == stored_user and check_password_hash(stored_hash, password)
                if ok:
                    return True
                return False
            except Exception:
                return False
        else:
            # No password hash set - deny login
            return False
    else:
        # Fallback to default credentials
        return username == 'admin' and password == 'password'
