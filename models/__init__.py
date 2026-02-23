"""
Database module for managing SQLite connections and initialization.
Handles all database setup, schema creation, and connection pooling.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import DATABASE, DEFAULT_SETTINGS


def get_db_connection():
    """
    Create and return a database connection with row factory enabled.
    Automatically creates/updates required tables on first call.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    # Create/migrate messages table - add mobile column if missing
    try:
        conn.execute("ALTER TABLE messages ADD COLUMN mobile TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create style_settings table if it doesn't exist
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS style_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            font_family TEXT NOT NULL DEFAULT 'Inter, sans-serif',
            font_color TEXT NOT NULL DEFAULT '#333333'
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Table already exists
    
    # Create social_links table if it doesn't exist
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS social_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL UNIQUE,
            icon TEXT NOT NULL,
            link_url TEXT NOT NULL
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Table already exists
    
    # Create doctors table if it doesn't exist
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            qualification TEXT NOT NULL,
            designation TEXT,
            image_path TEXT,
            status TEXT NOT NULL CHECK(status IN ('visible', 'hidden')) DEFAULT 'visible',
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Table already exists
    
    # Create settings table if it doesn't exist
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            website_name TEXT DEFAULT 'Medvika Pharmacy',
            website_description TEXT DEFAULT 'Trusted pharmacy delivering quality medicines with care',
            contact_email TEXT DEFAULT 'support@medvika.com',
            contact_phone TEXT DEFAULT '+91 9026805902',
            contact_address TEXT DEFAULT 'Delhi, India',
            business_hours TEXT DEFAULT 'Mon-Sun: 9:00 AM - 9:00 PM',
            footer_text TEXT DEFAULT 'Medvika Pharmacy - Your Trusted Healthcare Partner',
            footer_description TEXT DEFAULT 'Quality medicines delivered with care and responsibility',
            meta_description TEXT DEFAULT 'Online pharmacy delivering medicines',
            meta_keywords TEXT DEFAULT 'pharmacy, medicines, health',
            enable_gallery INTEGER DEFAULT 1,
            enable_contact INTEGER DEFAULT 1,
            enable_reviews INTEGER DEFAULT 1
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Table already exists
    
    # Ensure admin credential columns exist
    try:
        conn.execute("ALTER TABLE settings ADD COLUMN admin_username TEXT DEFAULT 'admin'")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    try:
        conn.execute("ALTER TABLE settings ADD COLUMN admin_password TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Ensure a default settings row exists with default admin password
    try:
        row = conn.execute('SELECT id, admin_password FROM settings WHERE id = 1').fetchone()
        if row is None:
            default_hash = generate_password_hash('1234')
            conn.execute('''INSERT INTO settings 
                (id, website_name, website_description, contact_email, contact_phone, contact_address,
                 business_hours, footer_text, footer_description, meta_description, meta_keywords, 
                 enable_gallery, enable_contact, enable_reviews, admin_username, admin_password)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (DEFAULT_SETTINGS['website_name'], DEFAULT_SETTINGS['website_description'], 
                 DEFAULT_SETTINGS['contact_email'], DEFAULT_SETTINGS['contact_phone'], 
                 DEFAULT_SETTINGS['contact_address'], DEFAULT_SETTINGS['business_hours'], 
                 DEFAULT_SETTINGS['footer_text'], DEFAULT_SETTINGS['footer_description'],
                 DEFAULT_SETTINGS['meta_description'], DEFAULT_SETTINGS['meta_keywords'], 
                 DEFAULT_SETTINGS['enable_gallery'], DEFAULT_SETTINGS['enable_contact'], 
                 DEFAULT_SETTINGS['enable_reviews'], 'admin', default_hash))
            conn.commit()
        else:
            # If admin_password is NULL, set default
            try:
                if not row['admin_password']:
                    conn.execute('UPDATE settings SET admin_password = ? WHERE id = 1', 
                               (generate_password_hash('1234'),))
                    conn.commit()
            except Exception:
                pass
    except Exception:
        pass
    
    return conn


def init_db():
    """
    Initialize the database by loading and executing schema.sql.
    Called once when the app starts if database doesn't exist.
    """
    if not os.path.exists(DATABASE):
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    conn = get_db_connection()
    try:
        with open('schema.sql') as f:
            conn.executescript(f.read())
        conn.close()
        print(f"Database initialized at {DATABASE}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.close()
