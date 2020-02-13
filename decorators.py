from functools import wraps
import output as op
import time
import sys

WAIT_TIME = 5

def retryable(max_tries):
    def outter(func):
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
        return inner
    return outter
