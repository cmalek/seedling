import os
# These are the env vars that get retrieved with getenv(). They must be set to avoid raising UnsetEnvironmentVariable.
os.environ['DB_NAME'] = ''
os.environ['DB_HOST'] = ''
os.environ['DB_USERj'] = ''
os.environ['DB_PASSWORD'] = ''
os.environ['CACHE'] = 'fake'
# These are set to True here ONLY so the static resouces for django-debug-toolbar will be collected during image build.
os.environ['DEVELOPMENT'] = 'True'
os.environ['ENABLE_DEBUG_TOOLBAR'] = 'True'

# noinspection PyUnresolvedReferences
from .settings import *  # noqa E402
