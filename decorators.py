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
            num_tries:int = 0
            function_name:str = func.__name__
            while num_tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    op.log_error(f"Decorator error --> {function_name}")
                    num_tries = num_tries + 1
                    time.sleep(WAIT_TIME)
            raise exceptions.NetworkException(f"Could not retrieve data from function {function_name} "
                                              f"values with {max_tries} re-tries")

        return inner

    return outter


def write_to_file(file_prefix: str):
    def outter(func):
        # noinspection PyUnresolvedReferences
        @wraps(func)
        def inner(*args, **kwargs):
            if WRITE_TO_FILE:
                now = datetime.datetime.now()
                date_now: str = now.strftime("%Y-%m-%d-%H-%M")
                file_path: str = os.path.join('.', "reports", f"{file_prefix}-{date_now}.txt")
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
