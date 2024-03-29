"""
Django settings for the seedling project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import environ
import logging
import logging.config
import sentry_sdk
import structlog
from seedling.logging import ConsoleRenderer
from sentry_sdk.integrations.django import DjangoIntegration

from .logging import censor_password_processor, request_context_logging_processor

# The name of our project
# ------------------------------------------------------------------------------
PROJECT_NAME = 'seedling'
HUMAN_PROJECT_NAME = 'Seedling'

# Load our environment with django-environ
BASE_DIR = environ.Path(__file__) - 2
APPS_DIR = BASE_DIR.path(PROJECT_NAME)

env = environ.Env()

# ==============================================================================

# DEBUG is Django's own config variable, while DEVELOPMENT is ours.
# Use DEVELOPMENT for things that you want to be able to enable/disable in dev
# without altering DEBUG, since that affects lots of other things.
DEBUG = env.bool('DEBUG', default=False)
DEVELOPMENT = env.bool('DEVELOPMENT', default=False)
TESTING = env.bool('TESTING', default=False)

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key
# You MUST define a unique DJANGO_SECRET_KEY env var for your app. And be sure not to use $ or # in the value.
# The default is there for tests ONLY.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='Z4peQSPAoo8fruA7pRXt2LefJD2lqYvXtgPFxF2hAeUd7NGOpA8fAt3UpnXpJ019')
# https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])

# INTERNATIONALIZATION (i18n) AND LOCALIZATION (l10n)
# Change these values to suit this project.
# https://docs.djangoproject.com/en/3.2/topics/i18n/
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = False
USE_L10N = False
USE_TZ = True
SITE_ID = 1

# DATABASES
# -----------
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
if TESTING:
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
            # This is needed in case the database doesn't have the newer default settings that enable "strict mode".
            'OPTIONS': {
                'sql_mode': 'traditional',
            }
        }
    }

# REDIS
# ------------------------------------------------------------------------------
REDIS_HOST = env('REDIS_HOST', default='redis')
REDIS_DB = env.int('REDIS_DB', default=0)

# CACHES
# ------------------------------------------------------------------------------
# Disable all caching if the optional DISABLE_CACHE env var is True.
if env.bool('DISABLE_CACHE', default=False):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        # … default cache config and others
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'redis://{REDIS_HOST}:6379/{REDIS_DB}',
            'TIMEOUT': 3600,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#root-urlconf
# noinspection PyUnresolvedReferences
ROOT_URLCONF = f'{PROJECT_NAME}.urls'
# https://docs.djangoproject.com/en/3.2/ref/settings/#wsgi-application
WSGI_APPLICATION = f'{PROJECT_NAME}.wsgi.application'

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.humanize', # Handy template tags
    'django.contrib.admin',
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    "allauth.socialaccount",
    'storages',
    'django_js_reverse',
    'django_extensions',
    'sass_processor',
    'wildewidgets',
    "rest_framework",
]
LOCAL_APPS = [
    # Local apps go here. Note that apps must be specified here as their full dotted form, just like how we do it with
    # wagtail, e.g. 'wagtail.admin'. Each of our apps' apps.py files set their respective "label" to their shortname,
    # which is how we can refer to models as e.g. 'users.CAPUser'.
    f'{PROJECT_NAME}.users',
    f'{PROJECT_NAME}.core',
    f'{PROJECT_NAME}.theme',
]
# https://docs.djangoproject.com/en/3.2/ref/settings/#installed-apps
# We need to have LOCAL_APPS first so our template overriding for third party and django apps will work
INSTALLED_APPS = LOCAL_APPS + DJANGO_APPS + THIRD_PARTY_APPS

# AUTHENTICATION
# ------------------------------------------------------------------------------
LOGIN_REDIRECT_URL = '/'
# https://docs.djangoproject.com/en/3.2/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Use our custom User model instead of auth.User, because it's good practice to define a custom one at the START.
AUTH_USER_MODEL = 'users.User'

# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# MIDDLEWARE
# ------------------------------------------------------------------------
MIDDLEWARE = [
    # Set our REMOTE_ADDR properly when we're behind a proxy.
    'xff.middleware.XForwardedForMiddleware',

    # Django's "default" middleware, in the appropriate order according to Django 2.0 docs.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Enables the use of the get_current_request() and get_current_user() functions.
    'crequest.middleware.CrequestMiddleware',
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#static-root
# noinspection PyUnresolvedReferences
STATIC_ROOT = '/static'
# https://docs.djangoproject.com/en/3.2/ref/settings/#static-url
STATIC_URL = f'/static/{PROJECT_NAME}/'
# https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = []
# https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-file-storage
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# https://docs.djangoproject.com/en/3.2/ref/settings/#media-root
# noinspection PyUnresolvedReferences
MEDIA_ROOT = '/media'
# https://docs.djangoproject.com/en/3.2/ref/settings/#media-url
MEDIA_URL = '/media/'


# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#templates
# The CACHE_TEMPLATES setting defaults to True, and tells Django to cache the template files it reads from disc in RAM.
# This radically increases performance, especially on docker when using shared volumes to keep your up-to-date code in
# the container, but it also means that the template cache sticks around until Gunicorn restarts. This complicates the
# development process for templates, so you are _generally_ recommended to set CACHE_TEMPLATES=False in your dev env.
# But because it makes _such_ a huge difference in docker-shared-volume performance, it's useful to leave it set to
# True when you're not actively doing template development.
CACHE_TEMPLATES = env.bool('CACHE_TEMPLATES', default=True)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            # Django does template caching for us correctly as long as OPTIONS['debug'] is False.
            'debug': not CACHE_TEMPLATES,
            # https://docs.djangoproject.com/en/3.2/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/3.2/ref/templates/api/#loader-types
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                "django.template.context_processors.media",
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR.path('fixtures')),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-proxy-ssl-header
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-ssl-redirect
# SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/2.0/ref/settings/#session-cookie-name
SESSION_COOKIE_NAME = f'{PROJECT_NAME}_session'
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/2.0/ref/settings/#csrf-cookie-name
CSRF_COOKIE_NAME = f'{PROJECT_NAME}_csrftoken'
# https://docs.djangoproject.com/en/3.0/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-trusted-origins
# We need this so that CSRF works behind our cloud proxy servers, because in that case we have Referer and Host header
# mismatches, and Django no likey.
CSRF_TRUSTED_ORIGINS = ['.caltech.edu']
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-secure
# CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#x-frame-options
X_FRAME_OPTIONS = 'DENY'
# https://docs.djangoproject.com/en/3.2/ref/settings/#session-expire-at-browser-close
# Don't use persistent sessions, since that could lead to a sensitive information leak.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-age
# Use two-hour session cookies, so that browsers configured to ignore the above setting (Chrome and Firefox... grumble)
# still only get cookies with a short lifespan. The two-hour session timer starts as of the user's last request.
SESSION_COOKIE_AGE = 60 * 120

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL', default=f'{HUMAN_PROJECT_NAME} <noreply@placodermi.org>')
# https://docs.djangoproject.com/en/3.2/ref/settings/#server-email
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/3.2/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default=f'[{HUMAN_PROJECT_NAME}]')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='mail')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default=None)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_PORT = env.int('EMAIL_PORT', default=1025)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = env('DJANGO_ADMIN_URL', default='admin/')
# https://docs.djangoproject.com/en/3.2/ref/settings/#admins
ADMINS = []
# https://docs.djangoproject.com/en/3.2/ref/settings/#managers
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
    cache_logger_on_first_use=False,
)

pre_chain = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt='iso'),
]

# Prevent Django from doing its own base logging config, since we need to replace its 'django' logger with our own.
LOGGING_CONFIG = None
# Build our custom logging config.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        # Set up the root logger to print to stderr using structlog. This will make all otherwise unconfigured
        # loggers print through structlog processor.
        # NOTE TO DEVS: If you are seeing duplicate logging, it may be because the root logger is using a different
        # handler than the logger you're sending messages to. Add `'propagate': False` to your logger to fix that.
        'handlers': ['structlog_console'],
        'level': 'INFO',
    },
    'loggers': {
        # DEVELOPER NOTE: If you define any more loggers here, you'll almost certainly want to use propagate: False.
        # Otherwise, if you tell that logger to use a different handler than the root logger, you'll get duplicated log
        # output.
        'django': {
            # When we set LOGGING_CONFIG = None above, we prevented the 'django' logger from being configured.
            # Thus, we must define it here so that we can configure it to only display log messages when DEVELOPMENT is
            # True (its default configuration makes it filter on DEBUG). This makes it print tracebacks and a few other
            # things during devel even when working with stuff that requires DEBUG to be False, and it retains its
            # original silence while running the tests. This is primarily important for printing tracebacks, which do
            # not print if sent to the structlog_console handler (probably because they are multiple lines).
            'handlers': ['devel_console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            # We don't care about attempts to access the site with a spoofed HTTP-HOST header. It clutters the logs.
            'handlers': ['null'],
            'propagate': False,
        },
        'qinspect': {
            # This is the QueryInspect logger. We always configure it (to simplify the logging setup code), but it
            # doesn't get used unless we turn on QueryInspect.
            'handlers': ['devel_console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'handlers': {
        'structlog_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'structlog'
        },
        'devel_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'structlog',
            'filters': ['require_development_true'],
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'filters': {
        'require_development_true': {
            '()': 'seedling.logging.RequireDevelopmentTrueFilter',
        },
    },
    'formatters': {
        # Set up a special formatter for our structlog output
        'structlog': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': ConsoleRenderer(
                # Remember to set the env var COLORED_LOGGING=True in dev, to make this colorize all the logs.
                # It needs to remain disabled in test/prod, though, so it doesn't mess with the ELK stack.
                colors=env.bool('COLORED_LOGGING', default=False),
                repr_native_str=False,
                newlines=True
            ),
            'foreign_pre_chain': pre_chain,
            'format': 'SYSLOG %(message)s',
        },
    },
}
# Execute our custom logging config. Django normally does this for us after this file is loaded, but since we set
# LOGGING_CONFIG = False so we could override some of django's default loggers, we need to load LOGGING ourselves.
logging.config.dictConfig(LOGGING)

# Do not log changes to the following models. The model's full app_label.ModelName string must be included.
# This setting is used by ADS's custom model change logging code. By default we skip logging changes to sessions and
UNLOGGED_MODELS = ['sessions.Session']

# Seedling
# ------------------------------------------------------------------------------
BOOTSTRAP_ALWAYS_MIGRATE = True

# unittest-xml-reporting
# ------------------------------------------------------------------------------
# https://github.com/xmlrunner/unittest-xml-reporting/tree/master/#django-support
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = 2
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_FILE_NAME = 'results.xml'

# django-site-multitenancy
# ------------------------------------------------------------------------------
MULTITENANCY_SITE_MODEL = 'multitenancy.Site'

# django-crispy-forms
# ------------------------------------------------------------------------------
# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "email"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = "seedling.users.adapters.AccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_ADAPTER = "seedling.users.adapters.SocialAccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
# Also: https://dev.to/gajesh/the-complete-django-allauth-guide-la3
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time',
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'en_US',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.12',
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# django-xff
# ------------------------------------------------------------------------------
XFF_TRUSTED_PROXY_DEPTH = env.int('XFF_TRUSTED_PROXY_DEPTH', default=1)
XFF_HEADER_REQUIRED = env.bool('XFF_HEADER_REQUIRED', default=False)

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
    # QUERY_INSPECT_TRACEBACK_ROOTS = ['/seedling/']

# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = env('SENTRY_URL', default=None)
if SENTRY_DSN:
    # https://sentry.io/for/django/
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )

# TESTING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-TEST_RUNNER
if TESTING:
    DEBUG = False
    # Silence certain loggers during tests, because they'd otherwise completely clog the output.
    logging.getLogger('elasticsearch').setLevel(logging.CRITICAL)
    # Set the root logger to only display WARNING logs and above during tests.
    logging.getLogger('').setLevel(logging.WARNING)
