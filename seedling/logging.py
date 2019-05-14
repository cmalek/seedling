from io import StringIO
import re
from six import string_types

import structlog
from structlog.dev import (_MISSING, _ColorfulStyles, _PlainStyles)
try:
    import colorama
except ImportError:
    colorama = None

from .utils import get_current_request


logger = structlog.get_logger('seedling')


def request_context_logging_processor(_, __, event_dict):
    """
    Adds extra runtime event info to our log messages based on the current request.

      ``username``: (string) the username of the logged in user, if user is logged in.
      ``site``: (string) the hostname of the current Site. Logs as 'celery/manage.py' when there's no current request.
      ``remote_ip``: the REMOTE_ADDR address. django-xff will handle properly setting this if we're behind a proxy
      ``superuser``: True if the current User is a superuser

    Does not overwrite any event info that's already been set in the logging call.
    """
    request = get_current_request()
    if request is not None:
        try:
            # django-xff will set this appropriately to the actual client IP when
            # we are behind a proxy
            client_ip = request.META['REMOTE_ADDR']
        except AttributeError:
            # Sometimes there will be a current request, but it's not a real request (during tests). If we can't get
            # the real client ip, just use a placeholder.
            client_ip = 'fake IP'
        event_dict.setdefault('remote_ip', client_ip)
        event_dict.setdefault('username', request.user.username or 'AnonymousUser')
        event_dict.setdefault('superuser', request.user.is_superuser)
    return event_dict


def censor_password_processor(_, __, event_dict):
    """
    Automatically censors any logging context key called "password", "password1", or "password2".
    """
    for password_key_name in ('password', 'password1', 'password2'):
        if password_key_name in event_dict:
            event_dict[password_key_name] = '*CENSORED*'
    return event_dict


def get_logger():
    """
    Deprecated. Rather than calling get_logger(), one should use "from core.logging import logger".
    """
    return logger


def log_compat(obj):
    """
    Convert the given object to a string that's compatible with the logger output.
    """
    # If obj isn't already a string, convert it to one.
    if not isinstance(obj, string_types):
        obj = repr(obj)
    return obj


class ConsoleRenderer(object):
    """
    ..note::

        I copied this from ``structlog.dev.ConsoleRenderer`` and changed it
        because I didn't like the way it formatted the log messages, and it offers
        no way to customize it. -- CPM

    Render `event_dict`, possibly in colors, and ordered.

    :param bool colors: Use colors for a nicer output.
    :param bool repr_native_str: When ``True``, :func:`repr()` is also applied
        to native strings (i.e. unicode on Python 3 and bytes on Python 2).
        Setting this to ``False`` is useful if you want to have human-readable
        non-ASCII output on Python 2.  The `event` key is *never*
        :func:`repr()` -ed.
    :param bool newlines: if ``False``, replace newlines with "``|||``"
    Requires the colorama_ package if *colors* is ``True``.
    .. _colorama: https://pypi.org/project/colorama/
    """
    def __init__(self, colors=False, repr_native_str=False, newlines=True):
        if colors is True:
            if colorama is None:
                raise SystemError(
                    _MISSING.format(
                        who=self.__class__.__name__ + " with `colors=True`",
                        package="colorama"
                    )
                )

            colorama.init()
            styles = _ColorfulStyles
        else:
            styles = _PlainStyles

        self.newlines = newlines
        self._styles = styles
        self._level_to_color = {
            "critical": styles.level_critical,
            "exception": styles.level_exception,
            "error": styles.level_error,
            "warn": styles.level_warn,
            "warning": styles.level_warn,
            "info": styles.level_info,
            "debug": styles.level_debug,
            "notset": styles.level_notset,
        }

        for key in self._level_to_color.keys():
            self._level_to_color[key] += styles.bright

        if repr_native_str is True:
            self._repr = repr
        else:
            def _repr(inst):
                if isinstance(inst, str):
                    return inst
                else:
                    return repr(inst)
            self._repr = _repr

    def color(self, msg, color):
        color_str = getattr(self._styles, color, None)
        if color_str is None:
            color_str = color
        return "{}{}{}".format(color_str, msg, self._styles.reset)

    def __call__(self, _, __, event_dict):
        """
        """
        sio = StringIO()

        ts = event_dict.pop("timestamp", None)
        if ts is not None:
            sio.write(self.color(str(ts), 'timestamp') + " ")
        level = event_dict.pop("level",  None)
        if level is not None:
            sio.write("[{}] ".format(self.color(level.upper(), self._level_to_color[level])))
        logger_name = event_dict.pop("logger", None)
        if logger_name is not None:
            sio.write("{}: ".format(self.color(logger_name, 'bright')))
        event = self.color(str(event_dict.pop("event").encode('utf8')), 'bright')
        if event_dict:
            event = event + " "
        sio.write(event)

        stack = event_dict.pop("stack", None)
        exc = event_dict.pop("exception", None)
        sio.write(" ".join(
            "{}={}".format(
                self.color(key, 'kv_key'),
                self.color(self._repr(event_dict[key]), 'kv_key')
            ) for key in sorted(event_dict.keys())
        ))

        if stack is not None:
            sio.write("\n" + stack)
            if exc is not None:
                sio.write("\n\n" + "=" * 79 + "\n")
        if exc is not None:
            sio.write("\n" + exc)

        if not self.newlines:
            msg = re.sub("\n", "|||", sio.getvalue())
        else:
            msg = sio.getvalue()
        return msg
