##################################################################################
# Django Config - This file should only include settings defined by Django itself.
##################################################################################
import os

import environ
import logging.config
import sentry_sdk
import structlog
from seedling.logging import (
    ConsoleRenderer,
    censor_password_processor,
    request_context_logging_processor,
)
from sentry_sdk.integrations.django import DjangoIntegration

# The name of our project
# ------------------------------------------------------------------------------
PROJECT_NAME = 'commuter_survey'
HUMAN_PROJECT_NAME = 'Caltech Commuter Survey'


BASE_DIR = (
    environ.Path(__file__) - 2
)  # (seedling/config/settings.py - 2 = seedling/)
APPS_DIR = BASE_DIR.path("seedling")
RUN_DIR = BASE_DIR.path("run")

env = environ.Env()

# If we have a .env file, read that here.
# OS environment variables take precedence over variables from .env
ENV_FILE_PATH = BASE_DIR('.env')
if os.path.exists(ENV_FILE_PATH):
    env.read_env(ENV_FILE_PATH)

DEBUG = env.bool('DEBUG', default=False)
DEVELOPMENT = env.bool('DEVELOPMENT', default=False)

# GENERAL
# ------------------------------------------------------------------------------
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="Z4peQSPAoo8fruA7pRXt2LefJD2lqYvXtgPFxF2hAeUd7NGOpA8fAt3UpnXpJ019",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# LOCALIZATION
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = False
USE_L10N = False
USE_TZ = True

# DATABASES
# -----------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
if env('TESTING', default=False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR.path('db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DB_NAME', None),
            'USER': env('DB_USER', default=None),
            'PASSWORD': env('DB_PASSWORD', default=None),
            'HOST': env('DB_HOST', default=None),
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': env.int('CONN_MAX_AGE', default=60),  # noqa F405
            'OPTIONS': {
                'sql_mode': 'STRICT_TRANS_TABLES',
                'isolation_level': 'read committed'
            }
        }
    }


# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# Disable all caching if the optional DISABLE_CACHE env var is True.
if env.bool('DISABLE_CACHE', default=False):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "baton",
    "django.contrib.admin",
    "baton.autodiscover"
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_framework",
    "multitenancy",
    "reversion",
]
LOCAL_APPS = [
    "seedling.users",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Use our custom User model instead of auth.User.
AUTH_USER_MODEL = 'users.User'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    # Set our REMOTE_ADDR properly when we're behind a proxy
    'xff.middleware.XForwardedForMiddleware',

    # Django's "default" middleware (sans CommonMiddleware), in the appropriate order according to Django 2.0 docs.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Enables the use of the multitenancy.utils.get_current_site() function
    'crequest.middleware.CrequestMiddleware',
    # Our middleware
    'multitenancy.middleware.SiteSelectingMiddleware',
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = '/static'
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR('static'))]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = '/media'
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
CACHE_TEMPLATES = env.bool('CACHE_TEMPLATES', default=True)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR.path('templates'))],
        'OPTIONS': {
            # Django does template caching for us correctly as long as OPTIONS['debug'] is False.
            'debug': not CACHE_TEMPLATES,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            'context_processors': [
                "django.template.context_processors.debug",
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap4"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)


# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
# SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/2.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['*'])
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"
# https://docs.djangoproject.com/en/2.2/ref/settings/#session-expire-at-browser-close
# Don't use persistent sessions, since that could lead to a sensitive information leak.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# https://docs.djangoproject.com/en/2.2/ref/settings/#session-cookie-age
# Use two-hour session cookies, so that browsers configured to ignore the above setting (Chrome and Firefox... grumble)
# still only get cookies with a short lifespan. The two-hour session timer starts as of the user's last request.
SESSION_COOKIE_AGE = 60 * 120

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)

# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", default="Seedling <noreply@placodermi.org>")
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default="[Seedling]")

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
# TODO: Need to read this out of the environment
ADMINS = [("""Chris Malek""", "cmalek@placodermi.org")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
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
    'disable_existing_loggers': True,
    'filters': {
        'require_development_true': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': require_DEVELOPMENT_true
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'structlog'
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
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
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
        'handlers': ['console'],
        'level': 'INFO',
    },
    'formatters': {
        # Set up a special formatter for our structlog output
        'structlog': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': ConsoleRenderer(
                colors=env.bool('COLORED_LOGGING', default=False),
                repr_native_str=False,
                newlines=not DEVELOPMENT
            ),
            'foreign_pre_chain': pre_chain,
            'format': 'SYSLOG %(message)s'
        }
    },
}
# Do not log changes to the following models. The model's full app_label.ModelName string must be included.
UNLOGGED_MODELS = ['sessions.Session']

# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "username"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = "seedling.users.adapters.AccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_ADAPTER = "seedling.users.adapters.SocialAccountAdapter"

# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
COMPRESS_ENABLED = env.bool("COMPRESS_ENABLED", default=True)
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]

# django-xff
# ------------------------------------------------------------------------------
XFF_TRUSTED_PROXY_DEPTH = env.int('XFF_TRUSTED_PROXY_DEPTH', default=1)
XFF_HEADER_REQUIRED = env.bool('XFF_HEADER_REQUIRED', default=False)

# django-bleach
# ------------------------------------------------------------------------------
# Allow only bold, italics, and linebreak tags in bleach-filtered outputs.
BLEACH_ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'br']

# django-site-multitenancy
# ------------------------------------------------------------------------------
MULTITENANCY_SITE_MODEL = 'multitenancy.Site'

# django-debug-toolbar
# ------------------------------------------------------------------------------
# We don't enable the debug toolbar unless DEVELOPMENT is also True.
ENABLE_DEBUG_TOOLBAR = DEVELOPMENT and env.bool('ENABLE_DEBUG_TOOLBAR', default=False)
if ENABLE_DEBUG_TOOLBAR:
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
    INSTALLED_APPS += ['debug_toolbar']  # noqa F405
    INSTALLED_APPS += ['template_profiler_panel']
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa F405
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'template_profiler_panel.panels.template.TemplateProfilerPanel'
    ]
    # https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TEMPLATE_CONTEXT': True,
        'SHOW_TOOLBAR_CALLBACK': lambda x: True
    }

# django-queryinspect
# ------------------------------------------------------------------------------
if DEVELOPMENT and env.bool('ENABLE_QUERYINSPECT', default=False):
    # Configure django-queryinspect
    MIDDLEWARE += ['qinspect.middleware.QueryInspectMiddleware']
    LOGGING['loggers']['qinspect'] = {
        'handlers': ['devel_console'],
        'level': 'DEBUG',
        'propagate': True,
    }
    # Whether the Query Inspector should do anything (default: False)
    QUERY_INSPECT_ENABLED = True
    # Whether to log the stats via Django logging (default: True)
    QUERY_INSPECT_LOG_STATS = True
    # Whether to add stats headers (default: True)
    QUERY_INSPECT_HEADER_STATS = False
    # Whether to log duplicate queries (default: False)
    QUERY_INSPECT_LOG_QUERIES = True
    # Whether to log queries that are above an absolute limit (default: None - disabled)
    QUERY_INSPECT_ABSOLUTE_LIMIT = 100  # in milliseconds
    # Whether to log queries that are more than X standard deviations above the mean query time (default: None)
    QUERY_INSPECT_STANDARD_DEVIATION_LIMIT = 2
    # Whether to include tracebacks in the logs (default: False)
    QUERY_INSPECT_LOG_TRACEBACKS = False
    # Uncomment this to filter traceback output to include only lines of our app's first-party code.
    # I personally don't find this useful, because the offending Python is sometimes actually somewhere in django core.
    # QUERY_INSPECT_TRACEBACK_ROOTS = ['/app/']


# django-extensions
# ------------------------------------------------------------------------------
if DEVELOPMENT:
    # https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
    INSTALLED_APPS += ['django_extensions']  # noqa F405

# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = env('SENTRY_URL', default=None)
if SENTRY_DSN:
    # https://sentry.io/for/django/
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )

# LOGGING (redux)
# ------------------------------------------------------------------------------
# We do this here, rather than up with the rest of the logging code, so that our development settings can tweak the
# LOGGING setting before it gets used to configure python's logging system.
logging.config.dictConfig(LOGGING)
