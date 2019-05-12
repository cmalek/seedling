import os
from django.core.wsgi import get_wsgi_application
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry

# Connection to the debug server is now handled by pydev_middleware. I've left this code here, commented out, because
# it's possible that we may need to debug into something at a lower level than the middleware at some point. Like
# django's bootstrap process, for instance.
# import sys
# from djunk.utils import getenv
# # If the environment is configured to enable remote debugging, attach to the configured remote debug server.
# # If REMOTE_DEBUG_ENABLED set to True, REMOTE_DEBUG_HOST and REMOTE_DEBUG_PORT are required.
# if getenv('REMOTE_DEBUG_ENABLED', False):
#     # We keep this import inside the REMOTE_DEBUG_ENABLED check because doing the import slows down the process,
#     # even if we don't call settrace().
#     import pydevd
#
#     # Attach to a Remote Debugger session running in PyCharm or PyDev on the configured host and port.
#     # NOTE: If no remote debug server is running, this call will hang for a while, then crash, and the exception
#     # handler will also crash.
#     # Be aware of this!
#     print('Debugging Enabled')
#     pydevd.settrace(
#         host=getenv('REMOTE_DEBUG_HOST'),
#         port=getenv('REMOTE_DEBUG_PORT'),
#         suspend=False
#     )

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seedling.settings.settings')

application = get_wsgi_application()

# Add WSGI middlware:
application = Sentry(application)
