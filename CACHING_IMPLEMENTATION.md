"""
SIMPLE IN-MEMORY CACHE IMPLEMENTATION
======================================

This shows the complete caching implementation for your Flask dashboard.

STEP 1: Add these functions to utils/helpers.py (at the top, after imports)
═════════════════════════════════════════════════════════════════════════════

import time  # ← ADD THIS IMPORT

# ===== SIMPLE IN-MEMORY CACHE =====

# Global cache storage: {key: {'data': value, 'timestamp': time}}
_cache = {}
CACHE_TIMEOUT = 10  # seconds (10 seconds for dashboard stats)


def cache_get(key):
    '''Get cached data if not expired. Returns None if expired or not found.'''
    if key not in _cache:
        return None
    
    cached_item = _cache[key]
    age = time.time() - cached_item['timestamp']
    
    if age > CACHE_TIMEOUT:
        del _cache[key]  # Cache expired
        return None
    
    return cached_item['data']


def cache_set(key, value):
    '''Store data in cache with current timestamp.'''
    _cache[key] = {'data': value, 'timestamp': time.time()}


def cache_clear(key=None):
    '''Clear specific cache key or all cache if key is None.'''
    global _cache
    if key is None:
        _cache = {}
    elif key in _cache:
        del _cache[key]


STEP 2: Update admin_dashboard() route in routes/admin.py
═════════════════════════════════════════════════════════════════════════════

OLD CODE:
─────────
@admin_bp.route('/dashboard')
@admin_login_required
def admin_dashboard():
    conn = get_db_connection()
    try:
        total_photos = conn.execute('SELECT COUNT(*) as c FROM admin_content WHERE media_type = "photo"').fetchone()['c']
        total_videos = conn.execute('SELECT COUNT(*) as c FROM admin_content WHERE media_type = "video"').fetchone()['c']
        new_messages = conn.execute('SELECT COUNT(*) as c FROM messages').fetchone()['c']
        recent_uploads = conn.execute('SELECT * FROM admin_content ORDER BY created_at DESC LIMIT 6').fetchall()
    except Exception:
        total_photos = 0
        total_videos = 0
        new_messages = 0
        recent_uploads = []
    finally:
        conn.close()

    visitors_today = '1,294'
    return render_template('admin/dashboard.html', ...)


NEW CODE (with cache):
──────────────────────
from utils.helpers import cache_get, cache_set  # ← ADD THIS IMPORT

@admin_bp.route('/dashboard')
@admin_login_required
def admin_dashboard():
    """Admin dashboard with cached statistics."""
    
    # Try to get cached stats (10-second cache)
    cached_stats = cache_get('dashboard_stats')
    if cached_stats is not None:
        total_photos = cached_stats['total_photos']
        total_videos = cached_stats['total_videos']
        new_messages = cached_stats['new_messages']
        recent_uploads = cached_stats['recent_uploads']
    else:
        # Cache missed, fetch from database
        conn = get_db_connection()
        try:
            total_photos = conn.execute('SELECT COUNT(*) as c FROM admin_content WHERE media_type = "photo"').fetchone()['c']
            total_videos = conn.execute('SELECT COUNT(*) as c FROM admin_content WHERE media_type = "video"').fetchone()['c']
            new_messages = conn.execute('SELECT COUNT(*) as c FROM messages').fetchone()['c']
            recent_uploads = conn.execute('SELECT * FROM admin_content ORDER BY created_at DESC LIMIT 6').fetchall()
        except Exception:
            total_photos = 0
            total_videos = 0
            new_messages = 0
            recent_uploads = []
        finally:
            conn.close()
        
        # Store in cache
        cache_set('dashboard_stats', {
            'total_photos': total_photos,
            'total_videos': total_videos,
            'new_messages': new_messages,
            'recent_uploads': recent_uploads
        })

    visitors_today = '1,294'
    return render_template('admin/dashboard.html',
                          total_photos=total_photos,
                          total_videos=total_videos,
                          new_messages=new_messages,
                          recent_uploads=recent_uploads,
                          visitors_today=visitors_today)


STEP 3: Clear cache on data changes (upload/delete)
════════════════════════════════════════════════════

Add cache_clear() calls in write operations:

In admin_upload() function (after successful insert):
    cache_clear('dashboard_stats')  # ← Clear cache when new content uploaded

In admin_delete() function (after successful delete):
    cache_clear('dashboard_stats')  # ← Clear cache when content deleted

In admin_manage() function (optional - doesn't modify data):
    # No cache clear needed - read-only operation


EXPLANATION (2-3 lines)
═══════════════════════

1. cache_get() checks if 10-second cache exists; returns None if expired
2. If data not cached, fetch from database and store with cache_set()
3. cache_clear() removes cache when uploads/deletes occur, forcing fresh query


CACHE STRUCTURE
═══════════════

_cache = {
    'dashboard_stats': {
        'data': {
            'total_photos': 42,
            'total_videos': 8,
            'new_messages': 15,
            'recent_uploads': [...]
        },
        'timestamp': 1707348000.123
    }
}


BENEFITS
════════

✅ Reduces database queries on dashboard views
✅ 10-second cache keeps data relatively fresh
✅ Simple Python-only (no Redis/Memcached needed)
✅ Cache auto-expires on timeout
✅ Automatically cleared on data writes
✅ Read-only operations benefit, writes invalidate cache


OPTIONAL: Different cache times for different data
═══════════════════════════════════════════════════

To have different cache timeouts:

def cache_get_with_timeout(key, timeout):
    if key not in _cache:
        return None
    cached_item = _cache[key]
    age = time.time() - cached_item['timestamp']
    if age > timeout:
        del _cache[key]
        return None
    return cached_item['data']

# Usage:
cached_stats = cache_get_with_timeout('dashboard_stats', 10)  # 10 sec
cached_gallery = cache_get_with_timeout('gallery_items', 30)  # 30 sec


TESTING
═══════

1. Open /admin/dashboard (first load - database query, caches data)
2. Refresh /admin/dashboard (within 10 seconds - uses cache, no DB query)
3. Wait 11 seconds, refresh again (cache expired, database query again)
4. Upload new content (cache clears, next dashboard view fetches fresh data)


IMPORTANT NOTES
═══════════════

✅ Cache is in-memory (lost on app restart)
✅ Not suitable for multi-process servers (only for single-process development)
✅ For production with multiple workers, use Redis or memcached
✅ Does NOT cache login/uploads/deletes (only read-only stats)
✅ Simple and beginner-friendly
✅ Works perfectly for single-server deployments

---
Generated: February 7, 2026
Status: READY FOR IMPLEMENTATION
"""
