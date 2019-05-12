##################################################################################
# Django Config - This file should only include settings defined by Django itself.
##################################################################################
import os

from environs import Env

env = Env()
env.read_env()

SETTINGS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(SETTINGS_DIR)
BASE_DIR = os.path.dirname(PROJECT_DIR)

DEBUG = env.bool('DEBUG', False)

INSTALLED_APPS = [
    # Site types. These have to be first, but the code in site_types.py must remove one (except during the image build).
    'seedling',

    'core',
    'custom_auth',

    'analytical',
    'raven.contrib.django.raven_compat',

    # Django apps.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    # HAS to be first, to make it possible to debug other middleware.
    'core.middleware.pydev_middleware',

    # HAS to be second, because other middleware read this one's shared data.
    'core.middleware.MiddlewareIterationCounter',

    # Set our REMOTE_ADDR properly when we're behind a proxy
    'xff.middleware.XForwardedForMiddleware',

    # Django's "default" middleware (sans CommonMiddleware), in the appropriate order according to Django 2.0 docs.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Enables the use of the get_current_request() and get_current_user() functions.
    'core.middleware.SeedlingCrequestMiddleware',
]

AUTHENTICATION_BACKENDS = ()

# Multitenant will be running on an indeterminate number of hosts, so all need to be allowed.
ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'seedling.urls'
WSGI_APPLICATION = 'seedling.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            # 2018-01-15 rrollins: I finally figured out the "right" way to configure template caching. Django does it
            # for us as long as OPTIONS['debug'] is False, so we set it to False by default. But in dev, you should
            # define NO_TEMPLATE_CACHING=True in your env file to force django not to cache templates.
            'debug': env.bool('NO_TEMPLATE_CACHING', False),
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static and media file handling.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
# noinspection PyUnresolvedReferences
STATIC_ROOT = '/static'
STATIC_URL = '/static/'
# noinspection PyUnresolvedReferences
MEDIA_ROOT = '/media'
MEDIA_URL = '/media/'

SECRET_KEY = env.str('SECRET_KEY')

# If you decide to use Memcached for your CACHES setting below, uncomment this line to tell Django to use cached
# sessions. If you don't use Memcached, though, Django will default to database-backed sessions, which need to be
# manually cleared out on a regular basis (see etc/dev/cron/daily/sessions.sh), and cause a DB hit on every request.
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# Don't use persistent sessions, since that could lead to a sensitive information leak.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Use two-hour session cookies, so that browsers configured to ignore the above setting (Chrome and Firefox... grumble)
# still only get cookies with a short lifespan. The two-hour session timer starts as of the user's last request.
SESSION_COOKIE_AGE = 60 * 120

# Tell Django that it's running behind a proxy.
USE_X_FORWARDED_HOST = True

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Use our custom User model instead of auth.User.
AUTH_USER_MODEL = 'custom_auth.User'
