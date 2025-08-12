import time
import logging

logger = logging.getLogger(__name__)


def timed_fn(logger=logger, name=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            logger.info(f"{name or fn.__name__} started")
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            logger.info(
                f"{name or fn.__name__} finished in {time.perf_counter() - start:.2f}s"
            )
            return result

        return wrapper

    return decorator
