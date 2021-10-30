#!/usr/bin/env python

import crython
import sentry_sdk

from django.core import management


@crython.job(expr="@daily")
def do_daily_job():
    # Example
    # management.call_command('flush', verbosity=0, interactive=False)
    pass


if __name__ == '__main__':
    crython.start()
    crython.join()
