import threading
from collections import defaultdict
from crequest.middleware import CrequestMiddleware
from django.core.exceptions import MiddlewareNotUsed
from djunk.utils import getenv


class SeedlingCrequestMiddleware(CrequestMiddleware):

    def __init__(self, get_response=None):
        # Skip this middleware if the middleware chain has already run at least once.
        if MiddlewareIterationCounter.get_iteration_count() >= 1:
            raise MiddlewareNotUsed
        super().__init__(get_response)


class MiddlewareIterationCounter():
    """
    This middleware exists to prevent problems SeedlingCrequestMiddleware from saving the request to the current thread
    more than once.  Rare edge cases can cause this to happen.

    By counting the interations of the middleware chain, we can subclass or rewrite problematic middleware to make them
    exclude themselves from internal executions of the middleware chain.
    """

    _iterations = defaultdict(int)

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        current_thread = threading.current_thread()
        # Increment the current thread's interation counter on ingress.
        self._iterations[current_thread] += 1
        response = self.get_response(request)
        # Decrement the current thread's interation counter on egress.
        self._iterations[current_thread] -= 1
        # If we're down to 0 interations, delete the counter to avoid a memory leak.
        if self._iterations[current_thread] == 0:
            del self._iterations[current_thread]
        return response

    @classmethod
    def get_iteration_count(cls):
        """
        Returns the iteration count for the current thread.

        Since ``cls._iterations`` is a defaultdict, this can safely be called before the first increment, which
        returns 0.
        """
        return cls._iterations[threading.current_thread()]


def pydev_middleware(get_response):
    """
    We define this middleware as a function, rather than a class, because we want to import pydevd at server start time,
    rather than at the beginning of each request. We can't do that in a class-based Middleware due to scoping issues.

    rrollins 2018-05-31: Or rather, we can, but it requires some stuff that I didn't discover until after I wrote this.
    """
    # One-time configuration and initialization, executed when gunicorn starts up.
    if not getenv('REMOTE_DEBUG_ENABLED', False):
        # Don't enable this middleware if REMOTE_DEBUG_ENABLED isn't True.
        raise MiddlewareNotUsed

    # Skip this middleware if the middleware chain has already run at least once.
    # This prevents pydevd.stoptrace() from being called too early during preview requests.
    if MiddlewareIterationCounter.get_iteration_count() >= 1:
        # DEV NOTE: Paradoxically, this middleware must go in MIDDLEWARE before MiddlewareIterationCounter, even though
        # it uses get_iteration_count(), because otherwise we couldn't debug MiddlewareIterationCounter itself. This
        # means that the above call to get_iteration_count() will in fact _create_ the entry in
        # MiddlewareIterationCounter._iterations (with a value of 0), due to it being a defaultdict. This is mind-bendy,
        # but it's exactly why MiddlewareIterationCounter._iterations is a defaultdict, instead of just a dict.
        raise MiddlewareNotUsed

    host = getenv('REMOTE_DEBUG_HOST')
    port = getenv('REMOTE_DEBUG_PORT')
    print(f'DEBUGGING ENABLED. Ensure that a PyCharm/PyDev debug server is running at {host}:{port}')
    # We do this import after the REMOTE_DEBUG_ENABLED check because simply performing the import slows down the
    # process, even if we don't call settrace().
    import pydevd

    def middleware(request):
        # Before the request, we hook into the debug server.
        print('Begining debuggable request...')
        try:
            pydevd.settrace(host=host, port=port, suspend=False, trace_only_current_thread=True)
        except AttributeError:
            print('Debugger was unable to connect to the debug server.')

        response = get_response(request)

        # Once the request is done, we disconnect from the debug server. This prevents the connection from being idle
        # between requests, avoiding difficult-to-diagnose annoyances caused by anything that kills idle TCP
        # connections (*cough* Docker for Mac) and also allowing manage.py commands to be debugged more easily.
        pydevd.stoptrace()

        return response

    return middleware
