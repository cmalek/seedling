#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seedling.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # This allows easy placement of apps within the interior seedling directory.
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_path, 'seedling'))

    # Copy sys.argv so we can remove --debug before sending it to execute_from_command_line.
    # This makes it so that when the runserver command starts another copy of this process
    # as part of it's auto-reload mechanism, the --debug will still be in sys.argv.
    argv = sys.argv[:]

    execute_from_command_line(argv)


if __name__ == '__main__':
    main()
