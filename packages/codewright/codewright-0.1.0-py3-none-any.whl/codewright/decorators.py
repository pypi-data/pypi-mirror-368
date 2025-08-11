import time
import functools


def timer(func):
    """A decorator that prints the execution time of the function it decorates."""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer


def retry(tries=3, delay=2, backoff=2):
    """A decorator to retry a function if it raises an exception."""

    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    msg = f"{e}, Retrying in {mdelay} seconds..."
                    print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)

        return wrapper_retry

    return decorator_retry


def cache(func):
    """A simple decorator to cache the results of a function call (memoization)."""
    cache_storage = {}

    @functools.wraps(func)
    def wrapper_cache(*args, **kwargs):
        cache_key = (args, tuple(sorted(kwargs.items())))
        if cache_key not in cache_storage:
            cache_storage[cache_key] = func(*args, **kwargs)
        return cache_storage[cache_key]

    return wrapper_cache
