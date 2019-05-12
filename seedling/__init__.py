# Ensures that the celery app is always imported when Django starts, so that @shared_task will use multitenant's app.
from .celery import app as celery_app

__all__ = ['celery_app']
__version__ = '1.3.8'

###################################################################################################################
# Uncomment this code to make all warnings print a full stacktrace. Quite useful when using `python -Wd manage.py`.
###################################################################################################################
# import traceback
# import warnings
# import sys
#
#
# def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
#
#     log = file if hasattr(file, 'write') else sys.stderr
#     traceback.print_stack(file=log)
#     log.write(warnings.formatwarning(message, category, filename, lineno, line))
#     log.write('\n')
#
# warnings.showwarning = warn_with_traceback
