import asyncio
from collections.abc import Awaitable, Iterable
from typing import TypeVar

from tqdm.asyncio import tqdm

T = TypeVar("T")


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
