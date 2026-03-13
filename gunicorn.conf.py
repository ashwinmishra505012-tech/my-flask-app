# Gunicorn configuration for production deployment

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, with a jitter
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "access.log"
errorlog = "error.log"

# Process naming
proc_name = "medvika_flask_app"

# Server mechanics
daemon = False
pidfile = "gunicorn.pid"
user = "www-data"  # Change for your system
group = "www-data"  # Change for your system
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS)
# keyfile = "/path/to/ssl/private.key"
# certfile = "/path/to/ssl/certificate.crt"

# Application
wsgi_module = "app:app"
callable = "app"