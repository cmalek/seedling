import sys
from crequest.middleware import CrequestMiddleware


try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

# ConnectionRefusedError doesn't exist in Python 2.x, but it's ultimate parent class in Python 3 is OSError, so we
# can define our own ConnectionRefusedError like this in order to avoid an import error in Python 2.
if sys.version_info[0] == 2:
    class ConnectionError(OSError):
        pass

    class ConnectionRefusedError(ConnectionError):
        pass


class NoCurrentRequestException(Exception):
    pass


def get_current_request(default=None, silent=True, label='__DEFAULT_LABEL__'):
    """
    Returns the current request. This is a more robust form of get_current_request, but it's not backwards compatible,
    so we gave it a different name.

    You can optionally use ``default`` to pass in a dummy request object to act as the default if there is no current
    request, e.g. when ``get_current_request()`` is called during a manage.py command.

    2019-09-24 rrollins: This version of get_current_request is backwards compatible with the old version, while
    offering the exception raising functionality of Multitenant's get_current_request2() when passed silent=False.

    :param default: (optional) a dummy request object
    :type default: an object that emulates a Django request object

    :param silent: If ``False``, raise an exception if CRequestMiddleware can't get us a request object.  Default: True
    :type silent: boolean

    :param label: If ``silent`` is ``False``, put this label in our exception message
    :type label: string

    :rtype: a Django request object
    """
    request = CrequestMiddleware.get_request(default)
    if request is None and not silent:
        raise NoCurrentRequestException(
            "{} failed because there is no current request. Try using FakeCurrentRequest.".format(label)
        )
    return request


def get_current_user(default=None):
    """
    Returns the user responsible for the current request.

    You can optionally use ``default`` to pass in a dummy request object to act as the default if there is no current
    request, e.g. when ``get_current_user()`` is called during a manage.py command.

    :param default: (optional) a dummy request object
    :type default: an object that emulates a Django request object

    :rtype: a settings.AUTH_USER_MODEL type object
    """
    try:
        return get_current_request().user
    except AttributeError:
        # There's no current request to grab a user from.
        return default

