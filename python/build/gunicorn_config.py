"""
Configuration for Gunicorn WSGI server for DailyStonks application.
"""
import os
import multiprocessing

# Server socket
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8080')
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Security settings
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# Process naming
proc_name = 'dailystonks'

# SSL Settings (if using HTTPS)
if os.environ.get('GUNICORN_USE_SSL', 'false').lower() == 'true':
    keyfile = os.environ.get('GUNICORN_SSL_KEY')
    certfile = os.environ.get('GUNICORN_SSL_CERT')
    ca_certs = os.environ.get('GUNICORN_SSL_CA')
    ssl_version = 'TLS'
    ciphers = 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256'
    do_handshake_on_connect = True

# Server hooks
def on_starting(server):
    """
    Log when the server starts.
    """
    import logging
    logging.info("Starting DailyStonks server...")

def on_exit(server):
    """
    Log when the server exits.
    """
    import logging
    logging.info("Shutting down DailyStonks server...")

def pre_fork(server, worker):
    """
    Pre-fork handler for the worker.
    """
    import logging
    logging.info(f"Pre-forking worker {worker.age}")

def post_fork(server, worker):
    """
    Post-fork handler for the worker.
    """
    import logging
    logging.info(f"Worker {worker.pid} forked")

def pre_exec(server):
    """
    Pre-execution handler.
    """
    import logging
    logging.info("Pre-execution phase")

def when_ready(server):
    """
    Execute when server is ready to receive requests.
    """
    import logging
    logging.info(f"Server is ready. Listening on: {bind}")

def worker_int(worker):
    """
    Handle SIGINT for worker.
    """
    import logging
    logging.info(f"Worker {worker.pid} received INT signal")

def worker_abort(worker):
    """
    Handle SIGABRT for worker.
    """
    import logging
    logging.error(f"Worker {worker.pid} received ABORT signal")

def worker_exit(server, worker):
    """
    Handle worker exit.
    """
    import logging
    logging.info(f"Worker {worker.pid} exited (age: {worker.age}, requests: {worker.processed})")

def child_exit(server, worker):
    """
    Handle child exit.
    """
    import logging
    logging.info(f"Worker {worker.pid} child process exited")