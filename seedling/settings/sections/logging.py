"""
Logging settings
----------------

Change out the default python logging stack with one based on structlog.  This
allows us to iteratively construct a log message with fields.
"""

import structlog
from core.logging import request_context_logging_processor, censor_password_processor
from djunk.logging_handlers import ConsoleRenderer
from environs import Env

env = Env()
env.read_env()

# Use structlog to ease the difficulty of adding context to log messages
# See https://structlog.readthedocs.io/en/stable/index.html
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        request_context_logging_processor,
        censor_password_processor,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

timestamper = structlog.processors.TimeStamper(fmt='iso')
pre_chain = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    timestamper,
]


# noinspection PyUnusedLocal
def require_DEVELOPMENT_true(record):
    """
    When used with django.utils.log.CallbackFilter, log messages will be skipped unless DEVELOPMENT is True.
    """
    # Must use a local import of 'settings' here because this file is part of defining settings. Fortunately, this
    # function isn't called until log messages actually get emitted.
    from django.conf import settings
    return settings.DEVELOPMENT


LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_development_true': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': require_DEVELOPMENT_true
        },
    },
    'handlers': {
        'structlog_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'plain'
        },
        'devel_console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'filters': ['require_development_true']
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            # When we set LOGGING_CONFIG = None above, we prevented the 'django' logger from being configured.
            # Thus, we must define it here so that we can configure it to only display log messages when DEVELOPMENT is
            # True (its default configuration makes it filter on DEBUG). This makes it print tracebacks and a few other
            # things during devel even when working with stuff that requires DEBUG to be False, and it retains its
            # original silence while running the tests. This is primarily important for printing tracebacks, which do
            # not print if sent to the structlog_console handler (probably because they are multiple lines).
            'handlers': ['devel_console'],
            'level': 'INFO',
        },
        'elasticsearch': {
            # Elasticsearch is super chatty.  We don't need to know so much about indexing individual things, but we
            # do want to know about errors.
            'handlers': ['structlog_console'],
            'level': 'ERROR',
        },
        'django.security.DisallowedHost': {
            # Don't log attempts to access the site with a spoofed HTTP-HOST header. It massively clutters the logs,
            # and we really don't care about this error.
            'handlers': ['null'],
            'propagate': False,
        },
    },
    'root': {
        # Set up the root logger to print to stderr using structlog. This will make all otherwise unconfigured loggers
        # print through structlog processor.
        'handlers': ['structlog_console'],
        'level': 'INFO',
    },
    'formatters': {
        'plain': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': ConsoleRenderer(
                colors=env.bool('COLORED_LOGGING', False),
                repr_native_str=False,
                newlines=True
            ),
            'foreign_pre_chain': pre_chain,
            'format': 'SYSLOG %(message)s'
        }
    },
}

RAVEN_CONFIG = {
    'dsn': env.url('SENTRY_URL', None),
    'release': '0.0.1',
}
