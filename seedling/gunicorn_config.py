import environ

env = environ.Env()

##### General #####
bind = 'unix:/tmp/app.sock'
workers = 8
worker_class = 'sync'
daemon = False
timeout = 300
worker_tmp_dir = '/tmp'
# requires futures module for threads > 1
threads = 1

##### Devel #####
reload = env.bool('GUNICORN_RELOAD', default=False)
# If remote debugging is enabled, set the timeout very high, so one can pause for a long time in the debugger.
# Also set the number of workers to 1, which improves the debugging experience by not overwhelming the remote debugger.

##### Logging #####
# 2021-07-16 rrollins: This replaces the old gunicorn_logging.conf file with a more maintainable code block.
logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'handlers': ['syslog_console'],
        'level': 'INFO',
    },
    'loggers': {
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['syslog_console'],
            'propagate': False,
            'qualname': 'gunicorn.error',
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['access_console'],
            'propagate': False,
            'qualname': 'gunicorn.access',
        },
    },
    'handlers': {
        'syslog_console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'syslog',
        },
        'access_console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'access_log',
        },
    },
    'formatters': {
        'syslog': {
            '()': 'seedling.logging.DockerFormatter',
            'fmt': 'SYSLOG %(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
        'access_log': {
            '()': 'seedling.logging.DockerFormatter',
            'fmt': 'GUNICORN_ACCESS %(asctime)s %(message)s',
        },
    },
}

##### statsd #####
# These settings need to have defaults provided, because dev sites don't use statsd.
_host = env('STATSD_HOST', default=None)
_port = env.int('STATSD_PORT', default=8125)
statsd_host = f'{_host}:{_port}' if (_host and _port) else None
statsd_prefix = env('STATSD_PREFIX', default=None)
