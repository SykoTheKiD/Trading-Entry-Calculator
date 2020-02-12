from functools import wraps
import output as op
import time
import sys

WAIT_TIME = 3

def retryable(max_tries, num_err_vals, default_value=sys.maxsize):
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
            return tuple([default_value for _ in len(num_err_vals)])
        return inner
    return outter
