# Gunicorn configuration file for Render.com
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
backlog = 2048

# Worker processes
# Limit workers on free tier to prevent memory issues
max_workers = multiprocessing.cpu_count() * 2 + 1
workers = int(os.getenv('WEB_CONCURRENCY', min(max_workers, 4)))  # Max 4 workers on free tier
worker_class = 'sync'
worker_connections = 1000
timeout = 180  # Increased for OpenAI API calls (image generation can take time)
keepalive = 5
graceful_timeout = 60  # Time to finish requests before force kill
max_requests = 1000  # Restart worker after 1000 requests (prevent memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'marketing-agent'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
preload_app = True  # Load app before forking workers (saves memory)
tmp_upload_dir = None

# SSL (Render handles this)
keyfile = None
certfile = None
