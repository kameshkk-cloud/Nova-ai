"""
NOVA Retry Utility
==================
Decorator and helper for retrying operations that may transiently fail
(network calls, speech recognition, LLM API calls, etc.).

Usage::

    from nova.utils.retry import retry

    @retry(max_attempts=3, backoff=1.5, on=(ConnectionError, TimeoutError))
    def flaky_call():
        ...
"""

from __future__ import annotations

import functools
import time
from typing import Callable, Sequence, Type

from nova.config.settings import MAX_RETRIES, RETRY_BACKOFF
from nova.utils import logger as log


def retry(
    max_attempts: int = MAX_RETRIES,
    backoff: float = RETRY_BACKOFF,
    on: Sequence[Type[BaseException]] = (Exception,),
    reraise: bool = True,
) -> Callable:
    """
    Decorator that retries the wrapped function on specified exceptions.

    Parameters
    ----------
    max_attempts : int
        Total number of tries (including the first call).
    backoff : float
        Multiplier applied to the wait time between retries.
        Wait = backoff ** (attempt - 1) seconds.
    on : tuple of exception types
        Only retry when one of these exceptions is raised.
    reraise : bool
        If True, re-raise the last exception after exhausting retries.
        If False, return None instead.
    """
    on_tuple = tuple(on)

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc: BaseException | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except on_tuple as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        wait = backoff ** (attempt - 1)
                        log.debug(
                            f"[retry] {fn.__name__} attempt {attempt}/{max_attempts} "
                            f"failed ({exc!r}), retrying in {wait:.1f}s …"
                        )
                        time.sleep(wait)
                    else:
                        log.warn(
                            f"[retry] {fn.__name__} failed after {max_attempts} attempts: {exc!r}"
                        )
            if reraise and last_exc is not None:
                raise last_exc
            return None

        return wrapper
    return decorator
