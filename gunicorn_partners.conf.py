# Gunicorn configuration for partners_onerai project

# Server socket
bind = "127.0.0.1:8001"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/partners_onerai/gunicorn_access.log"
errorlog = "/var/log/partners_onerai/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "partners_onerai_gunicorn"

# Server mechanics
daemon = False
pidfile = "/var/run/partners_onerai/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (uncomment when you have SSL certificates)
# keyfile = "/etc/ssl/private/partners.onerai.kz.key"
# certfile = "/etc/ssl/certs/partners.onerai.kz.crt"

# Environment
raw_env = [
    'DJANGO_SETTINGS_MODULE=partners_onerai.settings_production',
]

# Preload application for better performance
preload_app = True

# Worker process management
worker_tmp_dir = "/dev/shm"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
