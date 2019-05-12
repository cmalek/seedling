# This file exists to allow collectstatic to run during the docker build process. We can't set environment variables
# in the normal way during that process, so we set them here before importing settings.py
import os

# These are the env vars that get retrieved with getenv(). They must be set to avoid raising UnsetEnvironmentVariable.
os.environ['DB_NAME'] = 'fake'
os.environ['DB_USER'] = 'fake'
os.environ['DB_PASSWORD'] = 'fake'
os.environ['DB_HOST'] = 'fake'
os.environ['DB_PORT'] = 'fake'
os.environ['SENTRY_URL'] = 'https://fake:fake@sentry.io/fake'
os.environ['GOOGLE_MAPS_V3_APIKEY'] = 'fake'
# These are set to True here ONLY so the static resouces for django-debug-toolbar will be collected during image build.
os.environ['DEVELOPMENT'] = 'True'
os.environ['ENABLE_DEBUG_TOOLBAR'] = 'True'

# Lets the settings code that gets imported below know that we're currently building the image.
os.environ['IMAGE_BUILD'] = 'True'

# noinspection PyUnresolvedReferences
from .settings import *
