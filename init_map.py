import sqlite3
import os

db_path = 'instance/site.db'

# Create the table first if it doesn't exist
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create map_settings table
cursor.execute('''CREATE TABLE IF NOT EXISTS map_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    latitude REAL NOT NULL DEFAULT 28.404497,
    longitude REAL NOT NULL DEFAULT 77.203501,
    address TEXT NOT NULL DEFAULT 'Delhi, India',
    embed_url TEXT NOT NULL DEFAULT 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3887.3045159289506!2d77.20350961490706!3d28.404497892399254!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390ce62c7c8f1111%3A0x8f8f8f8f8f8f8f8f!2sDelhi!5e0!3m2!1sen!2sin!4v1706867000000',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)''')

# Insert default map settings
cursor.execute('''INSERT OR IGNORE INTO map_settings 
    (id, latitude, longitude, address, embed_url, updated_at) 
    VALUES (1, 28.404497, 77.203501, 'Delhi, India', 
    'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3887.3045159289506!2d77.20350961490706!3d28.404497892399254!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390ce62c7c8f1111%3A0x8f8f8f8f8f8f8f8f!2sDelhi!5e0!3m2!1sen!2sin!4v1706867000000', 
    CURRENT_TIMESTAMP)''')

conn.commit()
conn.close()

print('✅ Map settings table created and initialized successfully!')

