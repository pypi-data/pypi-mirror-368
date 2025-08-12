"""
Decorator function to log the time and changes in shape of the dataframe.
"""

import functools
import time


def log_decorator(func):
    @functools.wraps(func)
    def wrapper(df, *args, **kwargs):
        start_time = time.time()
        result = func(df, *args, **kwargs)
        stop_time = time.time()
        run_time = stop_time - start_time
        print(
            f"{func.__name__} finished in {run_time:.2f} seconds with {result.shape[0]} rows and {result.shape[1]} columns."
        )
        return result

    return wrapper
