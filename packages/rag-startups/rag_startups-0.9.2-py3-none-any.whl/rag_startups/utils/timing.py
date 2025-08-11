"""Timing decorator for performance monitoring."""

import functools
import time

from ..utils.output_formatter import formatter


def timing_decorator(func):
    """Decorator to measure and log execution time of functions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time

        # Add timing to our formatter
        formatter.add_timing(func.__name__, duration)

        return result

    return wrapper
