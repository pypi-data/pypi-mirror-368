import asyncio
from collections.abc import Awaitable
import contextlib
from dataclasses import dataclass
from typing import Callable, Coroutine, Iterable, Sequence, TypeVar, overload, cast
import inspect


T = TypeVar("T")


@dataclass(slots=True)
class WinnerInfo:
    """Metadata about the winning task.

    Attributes:
        index: Index of the winning factory in the input sequence.
        started_count: Number of tasks that had started when the winner completed.
        elapsed_s: Elapsed seconds from the first task start to winner completion.
    """

    index: int
    started_count: int
    elapsed_s: float


class AllTasksFailedError(Exception):
    """Raised when every raced task completes with an exception.

    Attributes:
        errors: The list of exceptions raised by each task that completed.
    """

    def __init__(self, errors: list[BaseException]):
        super().__init__("All raced tasks failed")
        self.errors = errors


async def _wait_first(
    call_factories: Sequence[Callable[[], Coroutine[object, object, T]]],
    *,
    started_flags: list[bool],
    accept: Callable[[T], bool] | None = None,
    cancel_pending: bool = True,
    total_timeout_s: float | None = None,
) -> tuple[T, WinnerInfo]:
    """Start the given call factories and return the first acceptable result.

    Args:
        call_factories: Zero-argument callables that each return an awaitable.
        accept: Optional predicate to validate a result. If provided and it
            returns False, the result is ignored and waiting continues.
        cancel_pending: Whether to cancel remaining tasks after a win.
        total_timeout_s: Optional overall timeout in seconds for all tasks.

    Returns:
        A tuple ``(result, WinnerInfo)`` where ``result`` is the winning value.

    Raises:
        ValueError: If ``call_factories`` is empty.
        TimeoutError: If ``total_timeout_s`` elapses before an acceptable result.
        AllTasksFailedError: If all tasks complete with exceptions.
    """

    if not call_factories:
        raise ValueError("call_factories must be non-empty")

    event_loop = asyncio.get_event_loop()
    started_at = event_loop.time()
    tasks: list[asyncio.Task[T]] = [
        asyncio.create_task(factory()) for factory in call_factories
    ]
    errors: list[BaseException] = []

    async def _cancel_pending(pending: Iterable[asyncio.Task[T]]) -> None:
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    try:
        timeout_cm = (
            asyncio.timeout(total_timeout_s)
            if total_timeout_s is not None
            else contextlib.nullcontext()
        )
        async with timeout_cm:
            pending = set(tasks)
            while pending:
                done, pending = await asyncio.wait(
                    pending, return_when=asyncio.FIRST_COMPLETED
                )
                for completed in done:
                    try:
                        result = await completed
                    except BaseException as exc:
                        errors.append(exc)
                        continue
                    if accept is None or accept(result):
                        if cancel_pending:
                            await _cancel_pending(pending)
                        elapsed = event_loop.time() - started_at
                        winner_index = tasks.index(completed)
                        # Determine how many tasks had actually started based on flags
                        # set by the hedging layer after any per-task delay.
                        started_count = sum(1 for f in started_flags if f)
                        return result, WinnerInfo(
                            index=winner_index,
                            started_count=started_count,
                            elapsed_s=elapsed,
                        )
            raise AllTasksFailedError(errors)
    finally:
        # Best-effort cleanup in case caller set cancel_pending=False
        for task in tasks:
            if not task.done():
                task.cancel()


async def hedge(
    factory: Callable[[], Awaitable[T]],
    *,
    delays_s: Sequence[float],
    accept: Callable[[T], bool] | None = None,
    cancel_pending: bool = True,
    total_timeout_s: float | None = None,
) -> tuple[T, WinnerInfo]:
    """Hedge a single factory with replication and required start delays (classic hedging/speculative retry).

    Args:
        factory: A zero-argument callable returning an awaitable (coroutine).
        delays_s: Per-replica start delays in seconds for the additional replicas.
            The first replica always starts at t=0, and for each value ``d`` in
            ``delays_s`` an additional replica is started after ``d`` seconds.
        accept: Optional predicate to validate a result. If provided and it
            returns False, the result is ignored and waiting continues.
        cancel_pending: Whether to cancel remaining tasks after a win.
        total_timeout_s: Optional overall timeout in seconds for all tasks.

    Returns:
        A tuple ``(result, WinnerInfo)`` where ``result`` is the winning value.

    Raises:
        ValueError: If ``delays_s`` is empty (no replicas beyond the immediate one).
        TimeoutError: If the timeout elapses before an acceptable result.
        AllTasksFailedError: If all tasks complete with exceptions.
    """
    effective_delays = list(delays_s)
    if len(effective_delays) == 0:
        # Still allow a single immediate attempt, but enforce an explicit API.
        # If the caller wants no hedging, pass an empty tuple? We choose to
        # require at least one delay to honor the request that delays are not optional.
        raise ValueError("delays_s must contain at least one delay value")
    factories: list[Callable[[], Awaitable[T]]] = [factory] * (
        1 + len(effective_delays)
    )
    start_delays: list[float] = [0.0] + effective_delays

    started_flags: list[bool] = [False] * len(factories)

    async def _instrumented_delayed_call(
        idx: int, delay: float, factory: Callable[[], Awaitable[T]]
    ) -> T:
        if delay > 0:
            await asyncio.sleep(delay)
        started_flags[idx] = True
        return await factory()

    delayed_factories: list[Callable[[], Coroutine[object, object, T]]] = [
        (lambda i=i, d=delay, f=factory: _instrumented_delayed_call(i, d, f))
        for i, (delay, factory) in enumerate(zip(start_delays, factories))
    ]

    return await _wait_first(
        delayed_factories,
        started_flags=started_flags,
        accept=accept,
        cancel_pending=cancel_pending,
        total_timeout_s=total_timeout_s,
    )


@overload
async def race(
    coros_with_delays: Sequence[tuple[Awaitable[T], float]],
    *,
    accept: Callable[[T], bool] | None = None,
    cancel_pending: bool = True,
    total_timeout_s: float | None = None,
) -> tuple[T, WinnerInfo]: ...


@overload
async def race(
    coros_with_delays: Sequence[Awaitable[T]],
    *,
    accept: Callable[[T], bool] | None = None,
    cancel_pending: bool = True,
    total_timeout_s: float | None = None,
) -> tuple[T, WinnerInfo]: ...


async def race(
    coros_with_delays: Sequence[tuple[Awaitable[T], float] | Awaitable[T]],
    *,
    accept: Callable[[T], bool] | None = None,
    cancel_pending: bool = True,
    total_timeout_s: float | None = None,
) -> tuple[T, WinnerInfo]:
    """Race a sequence of awaitables (coroutines), each with an explicit delay, or just awaitables (all delay=0.0).

    Args:
        coros_with_delays: A sequence of (awaitable, delay) pairs, or just awaitables (all delay=0.0).
        accept: Optional predicate to validate a result. If provided and it
            returns False, the result is ignored and waiting continues.
        cancel_pending: Whether to cancel remaining tasks after a win.
        total_timeout_s: Optional overall timeout in seconds for all tasks.

    Returns:
        A tuple ``(result, WinnerInfo)`` where ``result`` is the winning value.

    Raises:
        ValueError: If the input is empty.
        TimeoutError: If the timeout elapses before an acceptable result.
        AllTasksFailedError: If all tasks complete with exceptions.
    """
    seq = list(coros_with_delays)
    if not seq:
        raise ValueError("coros_with_delays must be non-empty")
    # Normalize inputs and build delayed factories that either await a coroutine
    # object (and close it on pre-await cancellation) or await a generic awaitable
    # after the configured delay.
    records: list[
        tuple[Awaitable[T], float, bool]
    ] = []  # (awaitable, delay, is_coro_obj)
    for item in seq:
        if isinstance(item, tuple):
            awaitable, delay = item
        else:
            awaitable, delay = item, 0.0
        is_coro_obj = inspect.iscoroutine(awaitable)
        records.append((awaitable, float(delay), is_coro_obj))

    started_flags: list[bool] = [False] * len(records)

    async def _instrumented_delayed_coro(
        idx: int, delay: float, coro: Coroutine[object, object, T]
    ) -> T:
        """Await a specific coroutine object after delay; close if cancelled pre-await.

        Note: only use this when `coro` is a coroutine object (not a Task/Future).
        """
        started_await = False
        try:
            if delay > 0:
                await asyncio.sleep(delay)
            started_flags[idx] = True
            started_await = True
            # At this point we must await the coroutine object, cancellation after this will propagate to it naturally.
            return await coro
        except asyncio.CancelledError:
            if not started_await:
                # The coroutine object would otherwise be GC'd unawaited so close it.
                with contextlib.suppress(Exception):
                    # coroutine objects have .close(). Tasks/Futures do not reach here
                    # because we only use this branch for real coroutine objects.
                    coro.close()
            raise

    async def _instrumented_delayed_awaitable(
        idx: int, delay: float, awaitable: Awaitable[T]
    ) -> T:
        if delay > 0:
            await asyncio.sleep(delay)
        started_flags[idx] = True
        return await awaitable

    delayed_factories: list[Callable[[], Coroutine[object, object, T]]] = []
    for i, (aw, delay, is_coro_obj) in enumerate(records):
        if is_coro_obj:
            delayed_factories.append(
                lambda i=i,
                d=delay,
                c=cast(Coroutine[object, object, T], aw): _instrumented_delayed_coro(
                    i, d, c
                )
            )
        else:
            delayed_factories.append(
                lambda i=i, d=delay, a=aw: _instrumented_delayed_awaitable(i, d, a)
            )

    return await _wait_first(
        delayed_factories,
        started_flags=started_flags,
        accept=accept,
        cancel_pending=cancel_pending,
        total_timeout_s=total_timeout_s,
    )


__all__ = [
    "race",
    "hedge",
    "WinnerInfo",
    "AllTasksFailedError",
]
