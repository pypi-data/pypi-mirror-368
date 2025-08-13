""" Module to time code execution. """
import time
from functools import wraps

def timeit(func):
    """Decorator that measures and prints the execution time of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'{func.__name__} took {end - start:.2f} seconds to run')
        return result
    return wrapper
