#################################################################
# Development Config
#################################################################
from environs import Env

env = Env()
env.read_env()

from .cache import CACHES
from .django import INSTALLED_APPS, MIDDLEWARE
from .logging import LOGGING
from .seedling import SITE_TYPE
from .wagtail import WAGTAILSEARCH_BACKENDS

# Note that every use of getenv() in this file is given a default fallback value. This is because none of these env
# vars should be set at all in production.

DEVELOPMENT = env.bool('DEVELOPMENT', False)

if DEVELOPMENT:
    # Useful info for syling custom admin pages. Not helpful to site users, though. Just developers.
    INSTALLED_APPS.append('wagtail.contrib.styleguide')
    # Don't send real emails during developmnent. Just print them to the console.
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    # If you want to disable password validation in development for some reason, uncoment this line.
    # AUTH_PASSWORD_VALIDATORS = []

    # Don't use Sentry during development.
    RAVEN_CONFIG = {}
    # Prevent Raven from complaining about being disabled.
    LOGGING['loggers']['raven.contrib.django.client.DjangoClient'] = {
        'handlers': ['null'],
        'propagate': False,
    }

    # When debugging queries, set ENABLE_DB_SCREAMING=True to make django print every query it runs.
    if getenv('ENABLE_DB_SCREAMING', False):
        LOGGING['loggers']['django.db.backends'] = {'level': 'DEBUG'}

    SERVER_EMAIL = DEFAULT_FROM_ADDRESS = WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = f'{SITE_TYPE}+dev@caltech.edu'
    EMAIL_SUBJECT_PREFIX = f'[{SITE_TYPE}-dev] '

# We don't enable the debug toolbar unless DEVELOPMENT is also True.
ENABLE_DEBUG_TOOLBAR = DEVELOPMENT and env.bool('ENABLE_DEBUG_TOOLBAR', False)

# Because configuring django-debug-toolbar is so complex, I've consolidated all the settings code for it into here.
# In addition, seedling/urls.py uses ENABLE_DEBUG_TOOLBAR to potentially enable the __debug__ views.
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
    INSTALLED_APPS.append('template_profiler_panel')
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
    MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')

    # Display the toolbar under all circumstances, since we don't even install it outside of DEVELOPMENT mode.
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda x: True
    }


if DEVELOPMENT and env.bool('ENABLE_QUERYINSPECT', False):
    # Configure django-queryinspect
    MIDDLEWARE.append('qinspect.middleware.QueryInspectMiddleware')
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
    # Uncomment this to filter traceback output to include only lines of own code, and wagtail's code.
    # I personally don't find this useful, because the offending Python is sometimes actually somewhere in django core.
    # QUERY_INSPECT_TRACEBACK_ROOTS = ['/seedling/', '/multitenant-ve/lib/python3.4/site-packages/wagtail']

if env.bool('TESTING', False):
    DEBUG = False

    # Use the much faster sqllite3 database during tests.
    # noinspection PyUnresolvedReferences

    if env.bool('USE_SQLITE', False):
        # noinspection PyUnresolvedReferences
        DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': 'simple_test_db',
           },
        }

    # Disbale the debugging middleware during tests, so that it won't interfere with debugging of the test code itself.
    # You can comment this out if you do actually need the debugging middleware for a certain test. Note, however,
    # that it will prevent debugging the test code.
    MIDDLEWARE.remove('core.middleware.pydev_middleware')

    CACHES['default']['KEY_PREFIX'] = 'test'
    CACHEOPS_ENABLED = False

    # Don't log anything below Warnings during tests, since they'll get printed to stdout, polluting the test output.
    # We do want the warns/errors, even though some of them (e.g. Permission Denied) will pollute the output, because
    # otherwise we'll never learn about any _unexecpted) errors that don't crash the test (this happens with
    # elasticsearch sometimes).
    LOGGING['root']['level'] = 'WARN'

    # Don't polute the dev search index with test search content.
    WAGTAILSEARCH_BACKENDS['default']['INDEX'] = 'test'

    # Don't use Sentry during testing.
    RAVEN_CONFIG = {}

    # Use a test runner that switches our DEFAULT_FILE_STORAGE setting from S3 to a temp folder on the local filesystem.
    TEST_RUNNER = 'seedling.test_runner.LocalStorageDiscoverRunner'

# Silence the "Setting unique=True on a ForeignKey has the same effect as using a OneToOneField" system check.
# We need to use a unique ForeignKey because Wagtail doesn't have a OneToOneField Panel.
SILENCED_SYSTEM_CHECKS = ['fields.W342']
