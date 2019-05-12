#!/usr/bin/env python
import os
import sys
from djunk.utils import getenv


if '--debug' in sys.argv:
    # We keep this import inside the --debug check because simply doing the import slows down the process,
    # even if we don't call settrace().
    import pydevd

    # Attach to a Remote Debugger session running in PyCharm or PyDev on the configured host and port.
    print('Attempting to enable debugging. If this hangs, the debug server isn\'t accessible.', file=sys.stderr)
    # If --debug is used, REMOTE_DEBUG_HOST and REMOTE_DEBUG_PORT are required environment variables.
    pydevd.settrace(
        host=getenv('REMOTE_DEBUG_HOST'),
        port=getenv('REMOTE_DEBUG_PORT'),
        suspend=False
    )
    print('Debugging Enabled', file=sys.stderr)
else:
    # When running a manage.py command without --debug, we must ensure that the rest of the code doesn't think we're
    # in debug mode, regardless of what the environment variables say.
    os.environ['REMOTE_DEBUG_ENABLED'] = 'False'

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multitenant.settings.settings')

    # Copy sys.argv so we can remove --debug before sending it to execute_from_command_line.
    # This makes it so that when the runserver command starts another copy of this process
    # as part of it's auto-reload mechanism, the --debug will still be in sys.argv.
    argv = sys.argv[:]
    if '--debug' in argv:
        argv.remove('--debug')

    from django.core.management import execute_from_command_line
    execute_from_command_line(argv)
