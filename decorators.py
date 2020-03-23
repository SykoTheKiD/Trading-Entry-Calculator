# TODO Format file
import datetime
import os
import sys
import time
from functools import wraps

import exceptions
import output as op
from config_loader import WRITE_TO_FILE

WAIT_TIME: int = 5


def retryable(max_tries: int):
    def outter(func):
        # noinspection PyBroadException,PyTypeChecker
        @wraps(func)
        def inner(*args, **kwargs):
            num_tries = 0
            while num_tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    op.log_error(f"Decorator error --> {func.__name__}")
                    num_tries = num_tries + 1
                    time.sleep(WAIT_TIME)
            raise exceptions.BarChartAPIException(f"Could not retrieve debt values with {max_tries} re-tries")

        return inner

    return outter


def write_to_file(file_prefix: str):
    def outter(func):
        # noinspection PyUnresolvedReferences
        @wraps(func)
        def inner(*args, **kwargs):
            if WRITE_TO_FILE:
                now = datetime.datetime.now()
                date_now = now.strftime("%Y-%m-%d-%H-%M")
                file_path = os.path.join('.', "reports", f"{file_prefix}-{date_now}.txt")
                original_std_out = sys.stdout
                sys.stdout = open(file_path, 'w+')
                func(*args, **kwargs)
                sys.stdout.close()
                sys.stdout = original_std_out
                sys.stdout = sys.stdout
            else:
                func(*args, **kwargs)
        return inner
    return outter
