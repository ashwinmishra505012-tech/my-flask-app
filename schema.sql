-- SQLite schema for pharmacy web app


-- New admin_content table for gallery management
CREATE TABLE IF NOT EXISTS admin_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_type TEXT NOT NULL CHECK(media_type IN ('photo', 'video')),
    file_path TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('visible', 'hidden')),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    mobile TEXT,
    message TEXT NOT NULL,
    sent_time TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS map_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    latitude REAL NOT NULL DEFAULT 28.404497,
    longitude REAL NOT NULL DEFAULT 77.203501,
    address TEXT NOT NULL DEFAULT 'Delhi, India',
    embed_url TEXT NOT NULL DEFAULT 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3887.3045159289506!2d77.20350961490706!3d28.404497892399254!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390ce62c7c8f1111%3A0x8f8f8f8f8f8f8f8f!2sDelhi!5e0!3m2!1sen!2sin!4v1706867000000',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS style_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    font_family TEXT NOT NULL DEFAULT 'Inter, sans-serif',
    font_color TEXT NOT NULL DEFAULT '#333333'
);

CREATE TABLE IF NOT EXISTS social_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL UNIQUE,
    icon TEXT NOT NULL,
    link_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    qualification TEXT NOT NULL,
    designation TEXT,
    image_path TEXT,
    status TEXT NOT NULL CHECK(status IN ('visible', 'hidden')) DEFAULT 'visible',
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
