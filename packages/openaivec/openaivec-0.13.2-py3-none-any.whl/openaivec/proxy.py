import asyncio
import threading
from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, Generic, List, Optional, TypeVar

S = TypeVar("S", bound=Hashable)
T = TypeVar("T")


class ProxyBase(Generic[S, T]):
    """Common utilities shared by BatchingMapProxy and AsyncBatchingMapProxy.

    Provides order-preserving deduplication and batch size normalization that
    depend only on ``batch_size`` and do not touch concurrency primitives.

    Attributes:
        batch_size: Optional mini-batch size hint used by implementations to
            split work into chunks. When unset or non-positive, implementations
            should process the entire input in a single call.
    """

    batch_size: Optional[int] = None  # subclasses may override via dataclass

    @staticmethod
    def __unique_in_order(seq: List[S]) -> List[S]:
        """Return unique items preserving their first-occurrence order.

        Args:
            seq (list[S]): Sequence of items which may contain duplicates.

        Returns:
            list[S]: A new list containing each distinct item from ``seq`` exactly
            once, in the order of their first occurrence.
        """
        seen: set[S] = set()
        out: List[S] = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    def __normalized_batch_size(self, total: int) -> int:
        """Compute the effective batch size used for processing.

        If ``batch_size`` is not set or non-positive, the entire ``total`` is
        processed in a single call.

        Args:
            total (int): Number of items intended to be processed.

        Returns:
            int: The positive batch size to use.
        """
        return self.batch_size if (self.batch_size and self.batch_size > 0) else total


@dataclass
class BatchingMapProxy(ProxyBase[S, T], Generic[S, T]):
    """Thread-safe local proxy that caches results of a mapping function.

    This proxy batches calls to the ``map_func`` you pass to ``map()`` (if
    ``batch_size`` is set),
    deduplicates inputs while preserving order, and ensures that concurrent calls do
    not duplicate work via an in-flight registry. All public behavior is preserved
    while minimizing redundant requests and maintaining input order in the output.

    Example:
        >>> from typing import List
        >>> p = BatchingMapProxy[int, str](batch_size=3)
        >>> def f(xs: List[int]) -> List[str]:
        ...     return [f"v:{x}" for x in xs]
        >>> p.map([1, 2, 2, 3, 4], f)
        ['v:1', 'v:2', 'v:2', 'v:3', 'v:4']
    """

    # Number of items to process per call to map_func. If None or <= 0, process all at once.
    batch_size: Optional[int] = None
    __cache: Dict[S, T] = field(default_factory=dict)
    # Thread-safety primitives (not part of public API)
    __lock: threading.RLock = field(default_factory=threading.RLock, repr=False)
    __inflight: Dict[S, threading.Event] = field(default_factory=dict, repr=False)

    # ---- private helpers -------------------------------------------------
    # expose base helpers under subclass private names for compatibility
    __unique_in_order = staticmethod(ProxyBase._ProxyBase__unique_in_order)
    __normalized_batch_size = ProxyBase._ProxyBase__normalized_batch_size

    def __all_cached(self, items: List[S]) -> bool:
        """Check whether all items are present in the cache.

        This method acquires the internal lock to perform a consistent check.

        Args:
            items (list[S]): Items to verify against the cache.

        Returns:
            bool: True if every item is already cached, False otherwise.
        """
        with self.__lock:
            return all(x in self.__cache for x in items)

    def __values(self, items: List[S]) -> List[T]:
        """Fetch cached values for ``items`` preserving the given order.

        This method acquires the internal lock while reading the cache.

        Args:
            items (list[S]): Items to retrieve from the cache.

        Returns:
            list[T]: The cached values corresponding to ``items`` in the same
            order.
        """
        with self.__lock:
            return [self.__cache[x] for x in items]

    def __acquire_ownership(self, items: List[S]) -> tuple[List[S], List[S]]:
        """Acquire ownership for missing items and identify keys to wait for.

        For each unique item, if it's already cached, it is ignored. If it's
        currently being computed by another thread (in-flight), it is added to
        the wait list. Otherwise, this method marks the key as in-flight and
        considers it "owned" by the current thread.

        Args:
            items (list[S]): Unique items (order-preserving) to be processed.

        Returns:
            tuple[list[S], list[S]]: A tuple ``(owned, wait_for)`` where
            - ``owned`` are items this thread is responsible for computing.
            - ``wait_for`` are items that another thread is already computing.
        """
        owned: List[S] = []
        wait_for: List[S] = []
        with self.__lock:
            for x in items:
                if x in self.__cache:
                    continue
                if x in self.__inflight:
                    wait_for.append(x)
                else:
                    self.__inflight[x] = threading.Event()
                    owned.append(x)
        return owned, wait_for

    def __finalize_success(self, to_call: List[S], results: List[T]) -> None:
        """Populate cache with results and signal completion events.

        Args:
            to_call (list[S]): Items that were computed.
            results (list[T]): Results corresponding to ``to_call`` in order.
        """
        if len(results) != len(to_call):
            # Prevent deadlocks if map_func violates the contract.
            # Release waiters and surface a clear error.
            self.__finalize_failure(to_call)
            raise ValueError("map_func must return a list of results with the same length and order as inputs")
        with self.__lock:
            for x, y in zip(to_call, results):
                self.__cache[x] = y
                ev = self.__inflight.pop(x, None)
                if ev:
                    ev.set()

    def __finalize_failure(self, to_call: List[S]) -> None:
        """Release in-flight events on failure to avoid deadlocks.

        Args:
            to_call (list[S]): Items that were intended to be computed when an
            error occurred.
        """
        with self.__lock:
            for x in to_call:
                ev = self.__inflight.pop(x, None)
                if ev:
                    ev.set()

    def clear(self) -> None:
        """Clear all cached results and release any in-flight waiters.

        Notes:
            - Intended to be called after all processing is finished.
            - Do not call concurrently with active map() calls to avoid
              unnecessary recomputation or racy wake-ups.
        """
        with self.__lock:
            for ev in self.__inflight.values():
                ev.set()
            self.__inflight.clear()
            self.__cache.clear()

    def close(self) -> None:
        """Alias for clear()."""
        self.clear()

    def __process_owned(self, owned: List[S], map_func: Callable[[List[S]], List[T]]) -> None:
        """Process owned items in mini-batches and fill the cache.

        Before calling ``map_func`` for each batch, the cache is re-checked
        to skip any items that may have been filled in the meantime. Items
        are accumulated across multiple original batches to maximize batch
        size utilization when some items are cached. On exceptions raised
        by ``map_func``, all corresponding in-flight events are released
        to prevent deadlocks, and the exception is propagated.

        Args:
            owned (list[S]): Items for which the current thread has computation
            ownership.

        Raises:
            Exception: Propagates any exception raised by ``map_func``.
        """
        if not owned:
            return
        batch_size = self.__normalized_batch_size(len(owned))

        # Accumulate uncached items to maximize batch size utilization
        pending_to_call: List[S] = []

        for i in range(0, len(owned), batch_size):
            batch = owned[i : i + batch_size]
            # Double-check cache right before processing
            with self.__lock:
                uncached_in_batch = [x for x in batch if x not in self.__cache]

            pending_to_call.extend(uncached_in_batch)

            # Process accumulated items when we reach batch_size or at the end
            is_last_batch = i + batch_size >= len(owned)
            if len(pending_to_call) >= batch_size or (is_last_batch and pending_to_call):
                # Take up to batch_size items to process
                to_call = pending_to_call[:batch_size]
                pending_to_call = pending_to_call[batch_size:]

                try:
                    results = map_func(to_call)
                except Exception:
                    self.__finalize_failure(to_call)
                    raise
                self.__finalize_success(to_call, results)

        # Process any remaining items
        while pending_to_call:
            to_call = pending_to_call[:batch_size]
            pending_to_call = pending_to_call[batch_size:]

            try:
                results = map_func(to_call)
            except Exception:
                self.__finalize_failure(to_call)
                raise
            self.__finalize_success(to_call, results)

    def __wait_for(self, keys: List[S], map_func: Callable[[List[S]], List[T]]) -> None:
        """Wait for other threads to complete computations for the given keys.

        If a key is neither cached nor in-flight, this method now claims ownership
        for that key immediately (registers an in-flight Event) and defers the
        computation so that all such rescued keys can be processed together in a
        single batched call to ``map_func`` after the scan completes. This avoids
        high-cost single-item calls.

        Args:
            keys (list[S]): Items whose computations are owned by other threads.
        """
        rescued: List[S] = []  # keys we claim to batch-process
        for x in keys:
            while True:
                with self.__lock:
                    if x in self.__cache:
                        break
                    ev = self.__inflight.get(x)
                    if ev is None:
                        # Not cached and no one computing; claim ownership to batch later.
                        self.__inflight[x] = threading.Event()
                        rescued.append(x)
                        break
                # Someone else is computing; wait for completion.
                ev.wait()
        # Batch-process rescued keys, if any
        if rescued:
            try:
                self.__process_owned(rescued, map_func)
            except Exception:
                # Ensure events are released on failure to avoid deadlock
                self.__finalize_failure(rescued)
                raise

    # ---- public API ------------------------------------------------------
    def map(self, items: List[S], map_func: Callable[[List[S]], List[T]]) -> List[T]:
        """Map ``items`` to values using caching and optional mini-batching.

        This method is thread-safe. It deduplicates inputs while preserving order,
        coordinates concurrent work to prevent duplicate computation, and processes
        owned items in mini-batches determined by ``batch_size``. Before each batch
        call to ``map_func``, the cache is re-checked to avoid redundant requests.

        Args:
            items (list[S]): Input items to map.
            map_func (Callable[[list[S]], list[T]]): Function that maps a batch of
                items to their corresponding results. Must return results in the
                same order as inputs.

        Returns:
            list[T]: Mapped values corresponding to ``items`` in the same order.

        Raises:
            Exception: Propagates any exception raised by ``map_func``.
        """
        if self.__all_cached(items):
            return self.__values(items)

        unique_items = self.__unique_in_order(items)
        owned, wait_for = self.__acquire_ownership(unique_items)

        self.__process_owned(owned, map_func)
        self.__wait_for(wait_for, map_func)

        return self.__values(items)


@dataclass
class AsyncBatchingMapProxy(ProxyBase[S, T], Generic[S, T]):
    """Asynchronous version of BatchingMapProxy for use with async functions.

    The ``map()`` method accepts an async ``map_func`` that may perform I/O and
    awaits it
    in mini-batches. It deduplicates inputs, maintains cache consistency, and
    coordinates concurrent coroutines to avoid duplicate work via an in-flight
    registry of asyncio events.

    Example:
        >>> import asyncio
        >>> from typing import List
        >>> p = AsyncBatchingMapProxy[int, str](batch_size=2)
        >>> async def af(xs: List[int]) -> List[str]:
        ...     await asyncio.sleep(0)
        ...     return [f"v:{x}" for x in xs]
        >>> async def run():
        ...     return await p.map([1, 2, 3], af)
        >>> asyncio.run(run())
        ['v:1', 'v:2', 'v:3']
    """

    batch_size: Optional[int] = None
    max_concurrency: int = 8

    # internals
    __cache: Dict[S, T] = field(default_factory=dict, repr=False)
    __lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)
    __inflight: Dict[S, asyncio.Event] = field(default_factory=dict, repr=False)
    __sema: Optional[asyncio.Semaphore] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize internal semaphore based on ``max_concurrency``.

        If ``max_concurrency`` is a positive integer, an ``asyncio.Semaphore``
        is created to limit the number of concurrent ``map_func`` calls across
        overlapping ``map`` invocations. When non-positive or ``None``, no
        semaphore is used and concurrency is unrestricted by this proxy.

        Notes:
            This method is invoked automatically by ``dataclasses`` after
            initialization and does not need to be called directly.
        """
        # Initialize semaphore if limiting is requested; non-positive disables limiting
        if self.max_concurrency and self.max_concurrency > 0:
            self.__sema = asyncio.Semaphore(self.max_concurrency)
        else:
            self.__sema = None

    # ---- private helpers -------------------------------------------------
    # expose base helpers under subclass private names for compatibility
    __unique_in_order = staticmethod(ProxyBase._ProxyBase__unique_in_order)
    __normalized_batch_size = ProxyBase._ProxyBase__normalized_batch_size

    async def __all_cached(self, items: List[S]) -> bool:
        """Check whether all items are present in the cache.

        This method acquires the internal asyncio lock for a consistent view
        of the cache.

        Args:
            items (list[S]): Items to verify against the cache.

        Returns:
            bool: True if every item in ``items`` is already cached, False otherwise.
        """
        async with self.__lock:
            return all(x in self.__cache for x in items)

    async def __values(self, items: List[S]) -> List[T]:
        """Get cached values for ``items`` preserving their given order.

        The internal asyncio lock is held while reading the cache to preserve
        consistency under concurrency.

        Args:
            items (list[S]): Items to read from the cache.

        Returns:
            list[T]: Cached values corresponding to ``items`` in the same order.
        """
        async with self.__lock:
            return [self.__cache[x] for x in items]

    async def __acquire_ownership(self, items: List[S]) -> tuple[List[S], List[S]]:
        """Acquire ownership for missing keys and identify keys to wait for.

        Args:
            items (list[S]): Unique items (order-preserving) to be processed.

        Returns:
            tuple[list[S], list[S]]: A tuple ``(owned, wait_for)`` where owned are
            keys this coroutine should compute, and wait_for are keys currently
            being computed elsewhere.
        """
        owned: List[S] = []
        wait_for: List[S] = []
        async with self.__lock:
            for x in items:
                if x in self.__cache:
                    continue
                if x in self.__inflight:
                    wait_for.append(x)
                else:
                    self.__inflight[x] = asyncio.Event()
                    owned.append(x)
        return owned, wait_for

    async def __finalize_success(self, to_call: List[S], results: List[T]) -> None:
        """Populate cache and signal completion for successfully computed keys.

        Args:
            to_call (list[S]): Items that were computed in the recent batch.
            results (list[T]): Results corresponding to ``to_call`` in order.
        """
        if len(results) != len(to_call):
            # Prevent deadlocks if map_func violates the contract.
            await self.__finalize_failure(to_call)
            raise ValueError("map_func must return a list of results with the same length and order as inputs")
        async with self.__lock:
            for x, y in zip(to_call, results):
                self.__cache[x] = y
                ev = self.__inflight.pop(x, None)
                if ev:
                    ev.set()

    async def __finalize_failure(self, to_call: List[S]) -> None:
        """Release in-flight events on failure to avoid deadlocks.

        Args:
            to_call (list[S]): Items whose computation failed; their waiters will
            be released.
        """
        async with self.__lock:
            for x in to_call:
                ev = self.__inflight.pop(x, None)
                if ev:
                    ev.set()

    async def clear(self) -> None:
        """Clear all cached results and release any in-flight waiters.

        Notes:
            - Intended to be awaited after all processing is finished.
            - Do not call concurrently with active map() calls to avoid
              unnecessary recomputation or racy wake-ups.
        """
        async with self.__lock:
            for ev in self.__inflight.values():
                ev.set()
            self.__inflight.clear()
            self.__cache.clear()

    async def aclose(self) -> None:
        """Alias for clear()."""
        await self.clear()

    async def __process_owned(self, owned: List[S], map_func: Callable[[List[S]], Awaitable[List[T]]]) -> None:
        """Process owned keys in mini-batches, re-checking cache before awaits.

        Before calling ``map_func`` for each batch, the cache is re-checked to
        skip any keys that may have been filled in the meantime. Items
        are accumulated across multiple original batches to maximize batch
        size utilization when some items are cached. On exceptions raised
        by ``map_func``, all corresponding in-flight events are released
        to prevent deadlocks, and the exception is propagated.

        Args:
            owned (list[S]): Items for which this coroutine holds computation
            ownership.

        Raises:
            Exception: Propagates any exception raised by ``map_func``.
        """
        if not owned:
            return
        batch_size = self.__normalized_batch_size(len(owned))

        # Accumulate uncached items to maximize batch size utilization
        pending_to_call: List[S] = []

        for i in range(0, len(owned), batch_size):
            batch = owned[i : i + batch_size]
            async with self.__lock:
                uncached_in_batch = [x for x in batch if x not in self.__cache]

            pending_to_call.extend(uncached_in_batch)

            # Process accumulated items when we reach batch_size or at the end
            is_last_batch = i + batch_size >= len(owned)
            if len(pending_to_call) >= batch_size or (is_last_batch and pending_to_call):
                # Take up to batch_size items to process
                to_call = pending_to_call[:batch_size]
                pending_to_call = pending_to_call[batch_size:]

                acquired = False
                try:
                    if self.__sema:
                        await self.__sema.acquire()
                        acquired = True
                    results = await map_func(to_call)
                except Exception:
                    await self.__finalize_failure(to_call)
                    raise
                finally:
                    if self.__sema and acquired:
                        self.__sema.release()
                await self.__finalize_success(to_call, results)

        # Process any remaining items
        while pending_to_call:
            to_call = pending_to_call[:batch_size]
            pending_to_call = pending_to_call[batch_size:]

            acquired = False
            try:
                if self.__sema:
                    await self.__sema.acquire()
                    acquired = True
                results = await map_func(to_call)
            except Exception:
                await self.__finalize_failure(to_call)
                raise
            finally:
                if self.__sema and acquired:
                    self.__sema.release()
            await self.__finalize_success(to_call, results)

    async def __wait_for(self, keys: List[S], map_func: Callable[[List[S]], Awaitable[List[T]]]) -> None:
        """Wait for computations owned by other coroutines to complete.

        If a key is neither cached nor in-flight, this method now claims ownership
        for that key immediately (registers an in-flight Event) and defers the
        computation so that all such rescued keys can be processed together in a
        single batched call to ``map_func`` after the scan completes. This avoids
        high-cost single-item calls.

        Args:
            keys (list[S]): Items whose computations are owned by other coroutines.
        """
        rescued: List[S] = []  # keys we claim to batch-process
        for x in keys:
            while True:
                async with self.__lock:
                    if x in self.__cache:
                        break
                    ev = self.__inflight.get(x)
                    if ev is None:
                        # Not cached and no one computing; claim ownership to batch later.
                        self.__inflight[x] = asyncio.Event()
                        rescued.append(x)
                        break
                # Someone else is computing; wait for completion.
                await ev.wait()
        # Batch-process rescued keys, if any
        if rescued:
            try:
                await self.__process_owned(rescued, map_func)
            except Exception:
                await self.__finalize_failure(rescued)
                raise

    # ---- public API ------------------------------------------------------
    async def map(self, items: List[S], map_func: Callable[[List[S]], Awaitable[List[T]]]) -> List[T]:
        """Async map with caching, de-duplication, and optional mini-batching.

        Args:
            items (list[S]): Input items to map.
            map_func (Callable[[list[S]], Awaitable[list[T]]]): Async function that
                maps a batch of items to their results, preserving input order.

        Returns:
            list[T]: Mapped values corresponding to ``items`` in the same order.
        """
        if await self.__all_cached(items):
            return await self.__values(items)

        unique_items = self.__unique_in_order(items)
        owned, wait_for = await self.__acquire_ownership(unique_items)

        await self.__process_owned(owned, map_func)
        await self.__wait_for(wait_for, map_func)

        return await self.__values(items)
