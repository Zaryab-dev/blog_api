import multiprocessing
import os

# Server socket - Use PORT env variable for App Runner compatibility
port = os.getenv("PORT", "8080")
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes - Optimized for App Runner (1 vCPU / 2GB RAM)
workers = int(os.getenv("GUNICORN_WORKERS", "3"))
worker_class = "gthread"  # Thread-based for better I/O handling
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 60
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "leather_api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
