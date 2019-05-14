import re
import os
from logging import Formatter


class DockerFormatter(Formatter):

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
        class=seedling.docker.DockerFormatter
        format="GUNICORN_ERRORLOG %(asctime)s [%(process)d] [%(levelname)s] %(message)s"
        datefmt="[%Y-%m-%d %H:%M:%S %z]"

        [formatter_docker_access]
        class=seedling.docker.DockerFormatter
        format="GUNICORN_ACCESS %(asctime)s %(message)s"
        datefmt="[%Y-%m-%d %H:%M:%S %z]"

    """

    def format(self, record):
        s = super(DockerFormatter, self).format(record)
        # If this is a development environment, don't reformat the logging output.
        if os.getenv('DEVELOPMENT', False):
            return s
        return re.sub("\n", "|||", s)
