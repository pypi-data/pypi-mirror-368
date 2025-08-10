"""Helper functions."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import functools
import logging
import random
from typing import Any

from aiohttp import ClientResponseError

from .exceptions import TimeoutExceededError

_LOGGER = logging.getLogger(__name__)


def retry(
    exceptions: Any = Exception,
    tries: int = -1,
    delay: float = 0,
    max_delay: int | None = None,
    backoff: int = 1,
    jitter: int | tuple[int, int] = 0,
    logger: Any = _LOGGER,
) -> Callable[..., Any]:
    """Retry Decorator.

    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logging_logger. if None, logging is disabled.
    :returns: the result of the f function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Add decorator."""

        @functools.wraps(func)
        async def newfn(*args: Any, **kwargs: Any) -> Any:
            """Load function."""
            _tries, _delay = tries, delay
            while _tries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as error:  # pylint: disable=broad-except
                    _tries -= 1
                    if not _tries:
                        logger.error("%s, timeout exceeded", ErrorMsg(error))
                        raise TimeoutExceededError(error) from error

                    if logger is not None:
                        logger.warning(
                            "%s, trying again in %s seconds", ErrorMsg(error), _delay
                        )

                    await asyncio.sleep(_delay)
                    _delay *= backoff

                    if isinstance(jitter, tuple):
                        _delay += random.uniform(*jitter)
                    else:
                        _delay += jitter

                    if max_delay is not None:
                        _delay = min(_delay, max_delay)

        return newfn

    return decorator


def ErrorMsg(error: ClientResponseError) -> str:
    domain = error.args[0]["exception"].get("domain", "unknown")
    code = error.args[0]["exception"].get("code", "unknown")
    errs = [
        (
            f"{err.get('name')}: {err.get('reason', 'unknown reason')}"
            if err.get("name")
            else err.get("reason", "unknown reason")
        )
        for err in error.args[0]["exception"].get("errors", [])
    ]

    return f"Bbox API throw an exception (domain: {domain}, code: {code}): {errs}"
