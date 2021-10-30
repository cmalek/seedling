import logging
import os
import re
from io import StringIO

from django.db.models import ManyToManyField, QuerySet
import environ
import structlog
from structlog.dev import (_ColorfulStyles, _PlainStyles)


logger = structlog.get_logger('seedling')


class ConsoleRenderer(object):
    """
    ..note::

        I copied this from ``structlog.dev.ConsoleRenderer`` and changed it
        because I didn't like the way it formatted the log messages, and it offers
        no way to customize it. -- CPM

    Render `event_dict`, possibly in colors, and ordered.
    :param bool colors: Use colors for a nicer output.
    :param bool repr_native_str: When ``True``, :func:`repr()` is also applied
        to native strings (i.e. str on Python 3 and unicode on Python 2).
        Setting this to ``False`` is useful if you want to have human-readable
        non-ASCII output on Python 2.  The `event` key is *never*
        :func:`repr()` -ed.
    :param bool newlines: if ``False``, replace newlines with "``|||``"
    Requires the colorama_ package if *colors* is ``True``.
    .. _colorama: https://pypi.org/project/colorama/
    """
    def __init__(self, colors=False, repr_native_str=False, newlines=True):
        if colors is True:
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
        sio = StringIO()

        # Format the timestamp directly into the log string.
        ts = event_dict.pop('timestamp', None)
        if ts:
            sio.write(self.color('{} '.format(ts), 'timestamp'))

        # Format the log level directly into the log string.
        level = event_dict.pop('level', None)
        if level:
            # Ensure that level is the same type of string as the keys in self._level_to_color.
            sio.write('[{}] '.format(self.color(level.upper(), self._level_to_color[level])))

        # Format the logger name directly into the log string.
        logger_name = event_dict.pop('logger', None)
        if logger_name:
            sio.write('{}: '.format(self.color(logger_name, 'bright')))

        # Format the event name into the log string, adding a space only if there is data from the event left to log.
        event = event_dict.pop('event')
        event = self.color(event, 'bright')
        if event_dict:
            event = event + " "
        sio.write(event)

        # Pull the stacktrace and exception info out of the event_dict, so we can format them into the log string
        # later, if they're relevant.
        stack = event_dict.pop('stack', None)
        exc = event_dict.pop('exception', None)

        if stack is not None:
            sio.write('\n' + stack)
            if exc is not None:
                sio.write('\n\n' + '=' * 79 + '\n')
        if exc is not None:
            sio.write('\n' + exc)

        # Add the remainder of the event data to the log string as key=value chunks.
        sio.write(' '.join(
            '{}={}'.format(self.color(key, 'kv_key'), self.color(event_dict[key], 'kv_value'))
            for key in sorted(event_dict.keys())
        ))

        if not self.newlines:
            msg = re.sub('\n', '|||', sio.getvalue())
        else:
            msg = sio.getvalue()
        return msg


def model_to_dict(instance, exclude_passwords=False):
    """
    Convert the given model instance to a dictionary keyed by field name.
    Pass in exclude_passwords = True to skip any field named "password". This is primarily useful to prevent
    hashed passwords from being logged when a User object is created or changed.
    """
    data = {}
    for f in instance._meta.get_fields():
        if isinstance(f, ManyToManyField) or (f.name == 'password' and exclude_passwords):
            continue

        if hasattr(f, 'value_from_object'):
            try:
                data[f.name] = f.value_from_object(instance)
            except:  # noqa
                # If anything goes wrong at this step, just ignore this field.
                pass
            else:
                if isinstance(data[f.name], QuerySet):
                    # Convert QuerySets to concrete lists, so they're printable and comparable (for logging).
                    data[f.name] = list(data[f.name].all())
        else:
            field_data = getattr(instance, f.name, None)
            try:
                # If this field is a manager, grab all the managed objects.
                field_data = list(field_data.all())
            except AttributeError:
                pass
            data[f.name] = field_data
    return data


def log_compat(obj):
    """
    Convert the given object to a string that's compatible with the logger output.
    """
    # If obj isn't already a string, convert it to one. We skip strings because we want "string", and not "u'string'".
    if not isinstance(obj, str):
        obj = repr(obj)
    return obj


def log_model_changes(logger, original, new):
    """
    Logs the changes made from the original instance to new instance to the specified logger.
    """
    original_dict = model_to_dict(original, exclude_passwords=True)
    new_dict = model_to_dict(new, exclude_passwords=True)

    changes = {}
    for field_name, original_value in original_dict.items():
        new_value = new_dict.get(field_name)
        try:
            if original_value != new_value:
                changes[field_name] = '"{}" -> "{}"'.format(original_value, new_value)
        except TypeError:
            # Some fields (e.g. dates) can potentially trigger this kind of error when being compared. If that happens,
            # there's not much we can do about it, so we just skip that field.
            pass
    if changes:
        if original._meta.label.endswith(('.User')):
            if 'last_login' in changes and len(changes) == 1:
                # Don't log changes that are only to the "last_login" field on a User model.
                # That field gets changed every time the user logs in, and we already log logins.
                return
            if 'password' in changes:
                # Don't log the new password hash
                changes['password'] = "__NEW_PASSWORD__"
        # Don't let the "model" keyword that we set manually on info() conflict with the "changes" dict, which can
        # happen when renaming a model in a migration.
        if 'model' in changes:
            changes['other_model'] = changes.pop('model')
        logger.info('model.update', model=original._meta.label, pk=original.pk, **changes)


def log_model_m2m_changes(logger, instance, action, model, pk_set):
    """
    Logs the changes made to an object's many-to-many fields to the specified logger.
    """
    # The post_add and post_remove signals get sent even if no changes are actually made by their respective actions
    # (e.g. when add()'ing an object that's already in the m2m relationship).
    # Since there are no changes, there's nothing to log.
    if not pk_set:
        return

    if action == "post_remove":
        removed_objects = model.objects.filter(pk__in=pk_set)
        logger.info(
            'model.m2m.delete',
            model=instance._meta.label,
            objects=", ".join(log_compat(obj) for obj in removed_objects),
            instance=log_compat(instance)
        )
    elif action == "post_add":
        added_objects = model.objects.filter(pk__in=pk_set)
        logger.info(
            'model.m2m.add',
            model=instance._meta.label,
            objects=", ".join(log_compat(obj) for obj in added_objects),
            instance=log_compat(instance)
        )


def log_new_model(logger, instance):
    """
    Logs the field values set on a newly-saved model instance to the specified logger.
    """
    kwargs = model_to_dict(instance, exclude_passwords=True)
    if 'model' not in kwargs:
        kwargs['model'] = instance._meta.label
    if 'event' in kwargs:
        # The first argument to logger.info() here is technically a kwarg called
        # 'event', so if kwargs also has a key in it called 'event', our
        # logger.info() call will raise an exception about duplicate keyword args
        kwargs['event_obj'] = kwargs['event']
        del kwargs['event']
    logger.info('model.create', instance=log_compat(instance), **kwargs)


def log_model_deletion(logger, instance):
    """
    Logs the deletion of this model instance to the specified logger.
    """
    kwargs = model_to_dict(instance, exclude_passwords=True)
    if 'event' in kwargs:
        # The first argument to logger.info() here is technically a kwarg called
        # 'event', so if kwargs also has a key in it called 'event', our
        # logger.info() call will raise an exception about duplicate keyword args
        kwargs['event_obj'] = kwargs['event']
        del kwargs['event']
    if 'model' in kwargs:
        # Some models have a "model" keyword, which needs to be removed for the same reason as 'event'.
        kwargs['model_obj'] = kwargs['model']
        del kwargs['model']
    logger.info('model.delete', model=instance._meta.label, instance=log_compat(instance), **kwargs)


class RequireDevelopmentTrueFilter(logging.Filter):
    """
    A logging filter that only prints log messages if the DEVELOPMENT env var is True.

    Use it like this in your LOGGING dict:
    'filters': {
        'require_development_true': {
            '()': 'seedling.logging.RequireDevelopmentTrueFilter',
        },
    },

    Set up a handler to use it like this:
    'handlers': {
        'devel_console': {
            # Use this handler for loggers that should only print stuff when the DEVELOPMENT env var is True.
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'filters': ['require_development_true'],
        },
    },
    """

    def filter(self, record):
        return environ.Env().bool('DEVELOPMENT', default=False)


class DockerFormatter(logging.Formatter):

    """
    This is a replacement for logging.Formatter which converts newlines in
    messages to "``|||``".  This formatter is primarily for places where we
    can't use our ``LoggerMixin``. class

    **Newlines**

    We convert newlines in messages to "``|||``" because, when outputting log
    messages from a Docker container, all logs from all processes get mingled in
    stdout/stderr, and the Docker logging subsystem breaks up the stdout stream
    into log messages by looking for newlines.

    If we have newlines in our message, that means that the docker logging subsystem
    will break our one message into many messages, and that's bad.

    Sample config for gunicorn:

        [loggers]
        keys=root,gunicorn.error,gunicorn.access

        [handlers]
        keys=console,error_console

        [formatters]
        keys=docker_error,docker_access

        [logger_root]
        level=INFO
        handlers=console

        [logger_gunicorn.error]
        level=ERROR
        handlers=error_console
        propagate=0
        qualname=gunicorn.error

        [logger_gunicorn.access]
        level=INFO
        handlers=console
        propagate=0
        qualname=gunicorn.access

        [handler_console]
        class=StreamHandler
        formatter=docker_access
        args=(sys.stdout, )

        [handler_error_console]
        class=StreamHandler
        formatter=docker_error
        args=(sys.stdout, )

        [formatter_docker_error]
        class=ads_decorators.logging.DockerFormatter.DockerFormatter
        format="GUNICORN_ERRORLOG %(asctime)s [%(process)d] [%(levelname)s] %(message)s"
        datefmt="[%Y-%m-%d %H:%M:%S %z]"

        [formatter_docker_access]
        class=ads_decorators.logging.DockerFormatter.DockerFormatter
        format="GUNICORN_ACCESS %(asctime)s %(message)s"
        datefmt="[%Y-%m-%d %H:%M:%S %z]"

    """

    def format(self, record):
        s = super(DockerFormatter, self).format(record)
        # If this is a development environment, don't reformat the logging output.
        if os.getenv('DEVELOPMENT', False):
            return s
        return re.sub("\n", "|||", s)


def request_context_logging_processor(_, __, event_dict):
    """
    Adds extra runtime event info to our log messages based on the current request.

      ``username``: (string) the username of the logged in user, if user is logged in.
      ``site``: (string) the hostname of the current Site. Logs as 'celery/manage.py' when there's no current request.
      ``remote_ip``: the REMOTE_ADDR address. django-xff will handle properly setting this if we're behind a proxy
      ``superuser``: True if the current User is a superuser

    Does not overwrite any event info that's already been set in the logging call.
    """
    # This is imported here to avoid a circular import which is triggered during the docker image build by the
    # imports in middleware.py
    from seedling.middleware import get_current_request
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
