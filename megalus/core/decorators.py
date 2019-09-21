import asyncio
from functools import wraps


def run_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if hasattr(asyncio, "run"):
            return asyncio.run(f(*args, **kwargs))
        else:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(f(*args, **kwargs))

    return wrapper
