import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
from typing import AsyncIterator, Generator, Iterator, TypeVar

from .asyncio import run_in_executor, run_in_threadpool
from .utils import DummyStopIteration, next_without_stop_iteration

T = TypeVar("T")


def preactivate(iterator: Iterator[T]) -> Iterator[T]:
    iterator = iter(iterator)
    prefetched = next(iterator)
    return _preactivate(prefetched, iterator)


def _preactivate(prefetched: T, iterator: Iterator[T]) -> Iterator[T]:
    yield prefetched
    yield from iterator


async def apreactivate(aiterator: AsyncIterator[T]) -> AsyncIterator[T]:
    aiterator = aiter(aiterator)
    prefetched = await anext(aiterator)
    return _apreactivate(prefetched, aiterator)


async def _apreactivate(prefetched: T, aiterator: AsyncIterator[T]) -> AsyncIterator[T]:
    yield prefetched
    async for it in aiterator:
        yield it


def aprefetch_iterator(iterator: Iterator[T]):
    p = ThreadPoolExecutor(1)
    iterator = iter(iterator)
    prefetched = run_in_executor(p, next_without_stop_iteration, iterator)

    return _aprefetch_iterator(iterator, p, prefetched)


async def _aprefetch_iterator(
    iterator: Iterator[T],
    p: ThreadPoolExecutor,
    prefetched: asyncio.Future[T],
):
    try:
        while True:
            try:
                ret = await prefetched
            except DummyStopIteration:
                break
            prefetched = run_in_executor(p, next_without_stop_iteration, iterator)
            yield ret
    finally:
        await run_in_threadpool(p.shutdown)


def prefetch_iterator(iterator: Iterator[T]):
    p = ThreadPoolExecutor(1)

    iterator = iter(iterator)
    prefetched = p.submit(next, iterator)

    return _prefetch_iterator(iterator, p, prefetched)


def _prefetch_iterator(
    iterator: Iterator[T],
    p: ThreadPoolExecutor,
    prefetched: Future[T],
) -> Generator[T, None, None]:
    with p:
        while True:
            try:
                rets = prefetched.result()
            except StopIteration:
                break
            prefetched = p.submit(next, iterator)
            yield rets


def aprefetch_aiterator(iterator: AsyncIterator[T]):
    iterator = aiter(iterator)
    prefetched = asyncio.create_task(anext(iterator))

    return _aprefetch_aiterator(iterator, prefetched)


async def _aprefetch_aiterator(
    iterator: Iterator[T],
    prefetched: asyncio.Task[T],
):
    while True:
        try:
            ret = await prefetched
        except StopAsyncIteration:
            break
        prefetched = asyncio.create_task(anext(iterator))
        yield ret


class BasePrefetcher:
    def __init__(self):
        self._p = ThreadPoolExecutor(1)
        self._future = None


class AsyncPrefetcher(BasePrefetcher):
    async def prefetch(self, func, *args, **kwargs):
        ret = None
        if self._future is not None:
            ret = await self._future
            self._future = None

        if func is None:
            return ret

        self._future = run_in_executor(self._p, func, *args, **kwargs)
        return ret

    async def __aenter__(self):
        self._p.__enter__()
        return self

    async def __aexit__(self, *args):
        await self.prefetch(None)
        self._p.__exit__(*args)


class Prefetcher(BasePrefetcher):
    def prefetch(self, func, *args, **kwargs):
        ret = None
        if self._future is not None:
            ret = self._future.result()
            self._future = None

        if func is None:
            return ret

        self._future = self._p.submit(func, *args, **kwargs)
        return ret

    def __enter__(self):
        self._p.__enter__()
        return self

    def __exit__(self, *args):
        self.prefetch(None)
        self._p.__exit__(*args)
