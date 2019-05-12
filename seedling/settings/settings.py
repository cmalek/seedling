import logging.config
# Import the app-specific settings from their individual files in app_settings.
from .sections.analytics import *  # NOQA
from .sections.database import *  # NOQA
from .sections.django import *  # NOQA
# sections.auth must come after sections.django because it imports validators from custom_auth, which will fail to
# import if it hasn't been installed yet.
from .sections.i18n import *  # NOQA
from .sections.logging import *  # NOQA
from .sections.seedling import *  # NOQA
from .sections.xff import *  # NOQA
# Development config has to go last because it overrides several settings from other files.
from .sections.development import *  # NOQA

PROJECT_NAME = 'seedling'

# We do this here, rather than in sections/logging.py, so that our development settings can tweak LOGGING before it
# gets used to configure python's logging system.
logging.config.dictConfig(LOGGING)  # NOQA

##########################################################################
# Various Other Third Party App Configs That Don't Deserve Their Own Files
##########################################################################
# Set up django-js-reverse.
JS_REVERSE_JS_VAR_NAME = 'URLs'
