"""
VISUAL FOLDER STRUCTURE & RELATIONSHIPS
========================================

This document shows the refactored folder structure and how files relate to each other.


PROJECT TREE
============

d:\medvika-web\
│
├── 📄 app.py                           [MAIN ENTRY POINT - 75 lines]
│   ├── Imports config, models, routes
│   ├── Creates Flask app
│   ├── Registers blueprints
│   ├── Sets up context processors
│   └── Handles errors
│
├── 📄 config.py                        [CONFIGURATION - 80 lines]
│   ├── SECRET_KEY
│   ├── DATABASE path
│   ├── UPLOAD_FOLDER paths
│   ├── ALLOWED file extensions
│   ├── PLATFORM_ICONS mapping
│   └── DEFAULT settings
│
├── 📂 models/                          [DATABASE LAYER]
│   ├── 📄 __init__.py                  [Database functions - 150 lines]
│   │   ├── get_db_connection()         ← Used by all routes
│   │   └── init_db()                   ← Called on startup
│   │
│   └── 📄 database.py                  [Placeholder]
│
├── 📂 routes/                          [ROUTE HANDLERS - Blueprints]
│   ├── 📄 __init__.py                  [Blueprint definitions]
│   │   ├── public_bp = Blueprint('public')
│   │   └── admin_bp = Blueprint('admin', url_prefix='/admin')
│   │
│   ├── 📄 public.py                    [Public routes - 100 lines]
│   │   ├── @public_bp.route('/')       → home()
│   │   ├── @public_bp.route('/about')  → about()
│   │   ├── @public_bp.route('/contact') → contact()
│   │   └── @public_bp.route('/gallery') → gallery()
│   │
│   └── 📄 admin.py                     [Admin routes - 450+ lines]
│       ├── @admin_bp.route('')        → admin_login()
│       ├── @admin_bp.route('/dashboard') → admin_dashboard()
│       ├── @admin_bp.route('/upload')   → admin_upload()
│       ├── @admin_bp.route('/manage')   → admin_manage()
│       ├── @admin_bp.route('/edit/<id>') → admin_edit()
│       ├── @admin_bp.route('/messages')  → admin_messages()
│       ├── @admin_bp.route('/map')       → admin_map()
│       ├── @admin_bp.route('/style')     → admin_style()
│       ├── @admin_bp.route('/link')      → admin_link()
│       └── @admin_bp.route('/settings')  → admin_settings()
│
├── 📂 utils/                           [UTILITY FUNCTIONS]
│   ├── 📄 __init__.py                  [Auth functions - 50 lines]
│   │   ├── admin_login_required(f)     ← Decorator for protected routes
│   │   └── verify_admin_credentials()  ← Check login
│   │
│   ├── 📄 auth.py                      [Auth placeholder]
│   │
│   └── 📄 helpers.py                   [Helper functions - 40 lines]
│       ├── allowed_file()              ← File validation
│       ├── is_allowed_image()          ← Image validation
│       ├── is_allowed_video()          ← Video validation
│       ├── get_platform_icon()         ← Social icon lookup
│       └── get_social_links()          ← Query DB for templates
│
├── 📂 static/                          [STATIC ASSETS - UNCHANGED]
│   ├── 📂 css/
│   │   ├── style.css
│   │   ├── navfooter.css
│   │   ├── custom-card.css
│   │   └── admin/
│   │
│   ├── 📂 js/
│   │   ├── home.js
│   │   ├── gallery.js
│   │   └── admin/
│   │
│   ├── 📂 img/
│   │   ├── icons/
│   │   └── jpeg/
│   │
│   └── 📂 uploads/
│       ├── 📂 photos/                  ← Uploaded images
│       └── 📂 videos/                  ← Uploaded videos
│
├── 📂 templates/                       [HTML TEMPLATES - UNCHANGED]
│   ├── base.html
│   ├── home.html
│   ├── about.html
│   ├── contact.html
│   ├── gallery.html
│   └── 📂 admin/
│       ├── dashboard.html
│       ├── upload.html
│       ├── manage.html
│       ├── edit.html
│       ├── messages.html
│       ├── login.html
│       ├── map.html
│       ├── style.html
│       ├── link.html
│       └── settings.html
│
├── 📂 instance/                        [INSTANCE DATA - UNCHANGED]
│   └── site.db                         ← SQLite database
│
├── 📄 schema.sql                       [DATABASE SCHEMA - UNCHANGED]
│
├── 📄 requirements.txt                 [DEPENDENCIES - UNCHANGED]
│
├── 📄 init_map.py                      [MAP INIT - UNCHANGED]
│
├── 📄 README.md                        [PROJECT README - UNCHANGED]
│
├── 📄 REFACTORING_GUIDE.md             [Detailed explanation]
│
├── 📄 REFACTORING_SUMMARY.md           [Quick overview]
│
└── 📄 DEPLOYMENT_GUIDE.md              [Production deployment]


IMPORT RELATIONSHIPS
====================

app.py
├── imports config
│   └── Uses: SECRET_KEY, DEBUG, DATABASE, UPLOAD_FOLDER_*, 
│            PLATFORM_ICONS, DEFAULT_SETTINGS
│
├── imports models
│   └── Uses: init_db(), get_db_connection()
│
├── imports utils.helpers
│   └── Uses: get_social_links()
│
└── imports routes (public_bp, admin_bp)
    │
    ├── routes/__init__.py defines blueprints
    │   ├── public_bp (no prefix)
    │   └── admin_bp (prefix=/admin)
    │
    ├── routes/public.py
    │   ├── imports config
    │   │   └── Uses: DEFAULT_MAP_SETTINGS
    │   │
    │   ├── imports models
    │   │   └── Uses: get_db_connection()
    │   │
    │   └── Uses: public_bp blueprint
    │
    └── routes/admin.py
        ├── imports config
        │   └── Uses: All constants
        │
        ├── imports models
        │   └── Uses: get_db_connection()
        │
        ├── imports utils.auth
        │   └── Uses: admin_login_required, verify_admin_credentials()
        │
        ├── imports utils.helpers
        │   └── Uses: allowed_file, is_allowed_image, is_allowed_video,
        │            get_platform_icon
        │
        └── Uses: admin_bp blueprint


DATABASE LAYER (models/__init__.py)
===================================

Functions accessed from:

get_db_connection()
├── Called by: routes/public.py (contact, gallery)
├── Called by: routes/admin.py (all admin routes)
├── Called by: utils/helpers.py (get_social_links)
└── Returns: SQLite connection with Row factory

init_db()
├── Called by: app.py on startup
├── Called by: app.py if __name__ == '__main__'
└── Creates: All database tables from schema.sql


ROUTES & URLS
=============

REQUEST → app.py → blueprints → route functions → models → database

Public Routes (no /prefix):
  GET  /                     public_bp.home()
  GET  /about                public_bp.about()
  GET  /contact              public_bp.contact()
  POST /contact              public_bp.contact()
  GET  /gallery              public_bp.gallery()

Admin Routes (/admin prefix):
  GET/POST /admin            admin_bp.admin_login()
  GET      /admin/dashboard  admin_bp.admin_dashboard()
  GET/POST /admin/upload     admin_bp.admin_upload()
  GET      /admin/manage     admin_bp.admin_manage()
  GET/POST /admin/edit/<id>  admin_bp.admin_edit()
  POST     /admin/update/<id>admin_bp.admin_update() [AJAX]
  POST     /admin/delete/<id>admin_bp.admin_delete() [AJAX]
  GET      /admin/messages   admin_bp.admin_messages()
  GET      /admin/message/count admin_bp.admin_message_count() [AJAX]
  POST     /admin/message/delete/<id> admin_bp.admin_delete_message()
  GET      /admin/map        admin_bp.admin_map()
  POST     /admin/map/update admin_bp.update_map()
  GET      /admin/style      admin_bp.admin_style()
  POST     /admin/style/save admin_bp.save_style()
  GET      /admin/link       admin_bp.admin_link()
  POST     /admin/link/add   admin_bp.admin_link_add() [AJAX]
  POST     /admin/link/update/<id> admin_bp.admin_link_update() [AJAX]
  POST     /admin/link/delete/<id> admin_bp.admin_link_delete() [AJAX]
  GET/POST /admin/settings   admin_bp.admin_settings()

Other Routes (app.py):
  GET /logout                (any endpoint).logout()


DATABASE TABLES
===============

admin_content
├── Columns: id, media_type, file_path, title, description, status, created_at, updated_at
├── Used by: routes/admin.py (upload, manage, edit, delete, gallery)
└── Accessed via: get_db_connection()

messages
├── Columns: id, name, email, mobile, message, sent_time
├── Used by: routes/public.py (contact), routes/admin.py (messages)
└── Accessed via: get_db_connection()

map_settings
├── Columns: id, latitude, longitude, address, embed_url, updated_at
├── Used by: routes/admin.py (map), routes/public.py (contact)
└── Accessed via: get_db_connection()

style_settings
├── Columns: id, font_family, font_color
├── Used by: routes/admin.py (style)
└── Accessed via: get_db_connection()

social_links
├── Columns: id, platform, icon, link_url
├── Used by: routes/admin.py (link), utils/helpers.py (get_social_links)
└── Accessed via: get_db_connection()

settings
├── Columns: id, website_name, website_description, contact_email, contact_phone,
│            contact_address, business_hours, footer_text, footer_description,
│            meta_description, meta_keywords, enable_gallery, enable_contact,
│            enable_reviews, admin_username, admin_password
├── Used by: routes/admin.py (settings, login), utils/auth.py (verify_admin_credentials)
└── Accessed via: get_db_connection()


AUTHENTICATION FLOW
===================

1. User navigates to /admin
   └→ routes/admin.py: admin_login() GET
   └→ render admin/login.html

2. User submits credentials
   └→ routes/admin.py: admin_login() POST
   └→ utils/auth.py: verify_admin_credentials(username, password)
      └→ models: get_db_connection()
      └→ database: SELECT admin_username, admin_password FROM settings
      └→ check_password_hash() validation
   └→ Set session['admin_logged_in'] = True
   └→ Redirect to /admin/dashboard

3. User access protected route (/admin/dashboard)
   └→ @admin_login_required decorator (from utils/auth.py)
   └→ Check: if 'admin_logged_in' not in session
      └→ Redirect to /admin (login)
   └→ Route allowed to execute

4. User clicks logout
   └→ /logout route
   └→ Clear session['admin_logged_in']
   └→ Redirect to /admin (login)


FILE UPLOAD FLOW
================

1. User navigates to /admin/upload (protected route)
   └→ @admin_login_required checks session
   └→ routes/admin.py: admin_upload() GET
   └→ render admin/upload.html form

2. User selects file and submits
   └→ routes/admin.py: admin_upload() POST
   └→ Validate: media_type, file, title, description
   └→ utils/helpers.py: is_allowed_image() or is_allowed_video()
   └→ secure_filename() from werkzeug
   └→ file.save(path) to static/uploads/photos or /videos
   └→ models: get_db_connection()
   └→ INSERT INTO admin_content
   └→ Success message
   └→ Reload form with all uploads listed

3. User can edit/delete/hide files
   └→ routes/admin.py: admin_edit(), admin_update(), admin_delete()
   └→ UPDATE/DELETE operations on admin_content
   └→ Physical files managed in static/uploads/


TEMPLATE CONTEXT
================

All templates have access to:

From inject_social_links() context processor:
├── social_links: List of social media links
│   └── Each: {id, platform, icon, link_url}
│
From each route function:
├── Route-specific variables (e.g., map_data, settings, content)
└── Flask built-in: request, session, url_for, etc.

Example in template:
    {% for link in social_links %}
        <a href="{{ link.link_url }}" class="{{ link.icon }}">
    {% endfor %}


FILE SIZE REFERENCE
===================

Old Structure:
    app.py: 741 lines (monolithic)

New Structure:
    app.py: 75 lines
    config.py: 80 lines
    models/__init__.py: 150 lines
    routes/__init__.py: 15 lines
    routes/public.py: 100 lines
    routes/admin.py: 450+ lines
    utils/__init__.py: 50 lines
    utils/helpers.py: 40 lines
    ─────────────────
    Total: ~950 lines (well-organized)

Key: Same functionality, better organized


DEPENDENCY GRAPH
================

External Dependencies (in requirements.txt):
    Flask 2.0+
    Werkzeug 2.0+
    Jinja2 3.0+
    (SQLite included in Python)

Internal Dependencies:
    app.py
    ├── config
    ├── models
    ├── routes
    │   ├── public
    │   └── admin
    │       ├── config
    │       ├── models
    │       ├── utils (auth, helpers)
    │       └── werkzeug (built-in)
    └── utils (helpers)
        ├── config
        └── models


SCALING CONSIDERATIONS
======================

The modular structure allows easy scaling:

Add new feature module:
    routes/api.py
    routes/blog.py
    routes/analytics.py

Add new database models:
    models/products.py
    models/orders.py
    models/users.py

Add new utilities:
    utils/validators.py
    utils/decorators.py
    utils/formatters.py

Add new middleware:
    middleware/auth.py
    middleware/logging.py

All without affecting existing code.


SUMMARY
=======

The refactored structure provides:
    ✅ Clear separation of concerns
    ✅ Easy to understand data flow
    ✅ Modular and extensible design
    ✅ Production-ready organization
    ✅ Ready for team collaboration
    ✅ Simple debugging and maintenance

Every file has a clear purpose.
Every function is in the right place.
Every dependency is explicit.

---
Generated: February 7, 2026
Status: ✅ COMPLETE
"""
