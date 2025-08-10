import itertools
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from typing import Generator, Generic, Iterable, Iterator, TypeVar

T = TypeVar("T")


def rate_limit_iterator(
    iterator: Iterator[T], iters_per_second: float, start: float | None = None
) -> Generator[T, None, None]:
    start = start or time.time()
    for i, it in enumerate(iterator):
        yield it
        time.sleep(max(0, (i / iters_per_second) - (time.time() - start)))


def fcfs_iterator(*iterators: Iterator[T]) -> Generator[tuple[int, T], None, None]:
    with ThreadPoolExecutor(len(iterators)) as p:
        iterators = {i: iter(it) for i, it in enumerate(iterators)}
        futures = {p.submit(next, it): i for i, it in iterators.items()}

        while futures:
            complete, _ = wait(futures.keys(), return_when=FIRST_COMPLETED)

            for future in complete:
                try:
                    ret = future.result()
                    i = futures[future]
                    futures[p.submit(next, iterators[i])] = i
                    yield i, ret
                except StopIteration:
                    pass
                finally:
                    del futures[future]


class _LockedIterator(Generic[T]):
    def __init__(self, iterator: Iterator[T], lock: threading.Lock):
        self._iterator = iterator
        self._lock = lock

    def __iter__(self) -> "_LockedIterator":
        return self

    def __next__(self) -> T:
        with self._lock:
            return next(self._iterator)

    def __copy__(self) -> "_LockedIterator":
        return _LockedIterator(self._iterator.__copy__(), self._lock)


def safetee(iterable: Iterator[T], n=2) -> tuple[_LockedIterator[T], ...]:
    lock = threading.Lock()
    return tuple(_LockedIterator(it, lock) for it in itertools.tee(iterable, n))
