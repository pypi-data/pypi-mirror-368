import asyncio
from collections.abc import Awaitable, Iterable
from typing import TypeVar

from httpx import (
    CloseError,
    ConnectError,
    ConnectTimeout,
    NetworkError,
    ReadError,
    ReadTimeout,
    RemoteProtocolError,
)
from requests.exceptions import RequestException, Timeout
from tenacity import retry_if_exception_type
from tqdm.asyncio import tqdm

T = TypeVar("T")


_BASE_CONNECTION_ERRORS = (
    # From requests
    Timeout,
    ConnectionError,
    RequestException,
    # From httpx
    ConnectError,
    ConnectTimeout,
    ReadTimeout,
    ReadError,
    NetworkError,
    RemoteProtocolError,
    CloseError,
)

retry_if_connection_error = retry_if_exception_type(_BASE_CONNECTION_ERRORS)


def create_retry_if_connection_error(*additional_exceptions):
    """Create a retry condition with base connection errors plus additional exceptions."""
    return retry_if_exception_type(_BASE_CONNECTION_ERRORS + additional_exceptions)


async def gather_with_concurrency(
    n: int | asyncio.Semaphore, coros: Iterable[Awaitable[T]], progress: bool = False
) -> list[T]:
    """
    Run asyncio.gather with a concurrency limit.

    SEE: https://stackoverflow.com/a/61478547/2392535
    """
    semaphore = asyncio.Semaphore(n) if isinstance(n, int) else n

    async def sem_coro(coro: Awaitable[T]) -> T:
        async with semaphore:
            return await coro

    if progress:
        return await tqdm.gather(
            *(sem_coro(c) for c in coros), desc="Gathering", ncols=0
        )

    return await asyncio.gather(*(sem_coro(c) for c in coros))
