#################################################################
# Development Config
#################################################################
from .base import *  # noqa
from .base import env

DEBUG = False

CACHES['default']['KEY_PREFIX'] = 'test'  # noqa

# Don't log anything below Warnings during tests, since they'll get printed to stdout, polluting the test output.
# We do want the warns/errors, even though some of them (e.g. Permission Denied) will pollute the output, because
# otherwise we'll never learn about any _unexecpted) errors that don't crash the test (this happens with
# elasticsearch sometimes).
LOGGING['root']['level'] = 'WARN'  # noqa

# Silence the "Setting unique=True on a ForeignKey has the same effect as using a OneToOneField" system check.
# We need to use a unique ForeignKey because Wagtail doesn't have a OneToOneField Panel.
SILENCED_SYSTEM_CHECKS = ['fields.W342']
