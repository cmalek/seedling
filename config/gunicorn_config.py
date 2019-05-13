import os
import environ

BASE_DIR = (
    environ.Path(__file__) - 2
)  # (seedling/config/gunicorn_config.py - 2 = seedling/)

env = environ.Env()

# If we have a .env file, read that here.
# OS environment variables take precedence over variables from .env
ENV_FILE_PATH = BASE_DIR('.env')
if os.path.exists(ENV_FILE_PATH):
    env.read_env(ENV_FILE_PATH)

# General settings.
bind = '0.0.0.0:9300'
workers = 8
worker_class = 'sync'
daemon = False
timeout = 300

# requires futures module for threads > 1.
threads = 1

# During development, this will cause the server to reload when the code changes.
# noinspection PyShadowingBuiltins
reload = env.bool('GUNICORN_RELOAD', default=False)

# If remote debugging is enabled set the timeout very high, so one can pause for a long time in the debugger.
# Also set the number of workers to 1, which improves the debugging experience by not overwhleming the remote debugger.
if env.bool('REMOTE_DEBUG_ENABLED', default=False):
    timeout = 9999
    workers = 1

# Logging.
accesslog = '-'
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
errorlog = '-'
syslog = False
